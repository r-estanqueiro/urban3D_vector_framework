"""
Supplementary Material SM2 — Statistical Analysis & Typology Identification

Pipeline:
  1. Load `BGRI_Complete_Metrics.csv` (output of SM1).
  2. Drop blocks with NaN in MBV / HVC / svf_mean (816 of 822 valid).
  3. Z-score the three metrics.
  4. Diagnostic correlation matrix + PCA.
  5. K-Means inertia for k = 2..9 (elbow method).
  6. K-Means with k = 5 (n_init=20, random_state=42); reorder clusters by descending mean MBV.
  7. Consensus clustering: 500 iterations, 80% subsampling, average-linkage on 1 - C.
  8. Per-block consensus score + 'Stable' / 'Ambiguous' / 'Uncertain' category.

Determinism: a NumPy `default_rng(SEED)` seeds all subsample draws and is the only
source of randomness in this script (KMeans uses `random_state=42` for the canonical
fit and `random_state=it` per consensus iteration). Re-running this script with the
same SEED reproduces ARI ~ 0.9445 exactly.

Inputs (./input/):
  - BGRI_Complete_Metrics.csv

Outputs (./output/):
  - BGRI_Final_Typology_k5_Production.csv  cluster_ordered, consensus_ordered,
                                           consensus_score, consensus_category, *_z metrics
  - consensus_matrix_k5.npy                816x816 consensus matrix (loaded by fig 04)
  - inertia_k2_to_9.npy                    inertia values for elbow plot (loaded by fig 03)

Run: python SM2_Code_Typology_Consensus.py    (with .venv activated, from final/SM2/)
Software author: Rossana Estanqueiro <rossana.estanqueiro@fcsh.unl.pt>
Accompanying manuscript (submitted) co-authored with Carla Rebelo and José António Tenedório.
License: MIT
"""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).parent
INPUT_CSV = SCRIPT_DIR / "input" / "BGRI_Complete_Metrics.csv"
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_CSV = OUTPUT_DIR / "BGRI_Final_Typology_k5_Production.csv"
CONSENSUS_NPY = OUTPUT_DIR / "consensus_matrix_k5.npy"
INERTIA_NPY = OUTPUT_DIR / "inertia_k2_to_9.npy"

FEATURES = ["MBV", "HVC", "svf_mean"]
K = 5
N_ITER = 500
SUBSAMPLE = 0.8
SEED = 42


def main() -> None:
    print("SM2 — K-Means + 500-iteration consensus")
    print("=" * 60)

    df = pd.read_csv(INPUT_CSV)
    df = df.dropna(subset=FEATURES).reset_index(drop=True).copy()
    print(f"Valid blocks: {len(df)}")

    scaler = StandardScaler()
    X = scaler.fit_transform(df[FEATURES].values)
    for i, f in enumerate(FEATURES):
        df[f"{f}_z"] = X[:, i]

    print("\nPearson correlations:")
    print(df[FEATURES].corr().round(3))

    pca = PCA().fit(X)
    print(f"\nPCA explained variance: {np.round(pca.explained_variance_ratio_, 3)}")

    print("\nElbow method (k = 2..9):")
    inertia = np.array(
        [KMeans(n_clusters=k, n_init=20, random_state=SEED).fit(X).inertia_ for k in range(2, 10)]
    )
    print(f"  inertia: {np.round(inertia, 1)}")
    np.save(INERTIA_NPY, inertia)

    print(f"\nFitting K-Means (k={K}) and reordering clusters by descending MBV ...")
    kmeans = KMeans(n_clusters=K, n_init=20, random_state=SEED).fit(X)
    df["cluster_id"] = kmeans.labels_ + 1
    mbv_means = df.groupby("cluster_id")["MBV"].mean().sort_values(ascending=False)
    remap = {old: new for new, old in enumerate(mbv_means.index, start=1)}
    df["cluster_ordered"] = df["cluster_id"].map(remap)

    print(f"\nConsensus clustering: {N_ITER} iterations, {int(SUBSAMPLE*100)}% subsampling")
    n = len(df)
    co = np.zeros((n, n))
    counts = np.zeros((n, n))
    n_sub = int(n * SUBSAMPLE)
    rng = np.random.default_rng(SEED)
    for it in range(N_ITER):
        if (it + 1) % 100 == 0:
            print(f"  iter {it + 1}/{N_ITER}")
        idx = rng.choice(n, n_sub, replace=False)
        labels = KMeans(n_clusters=K, n_init=20, random_state=it).fit_predict(X[idx])
        for i in range(n_sub):
            for j in range(i + 1, n_sub):
                ii, jj = idx[i], idx[j]
                counts[ii, jj] += 1
                counts[jj, ii] += 1
                if labels[i] == labels[j]:
                    co[ii, jj] += 1
                    co[jj, ii] += 1

    consensus = np.divide(co, counts, out=np.zeros_like(co), where=counts != 0)
    np.fill_diagonal(consensus, 1.0)
    np.save(CONSENSUS_NPY, consensus)

    Z = linkage(squareform(1 - consensus), method="average")
    consensus_labels = fcluster(Z, t=K, criterion="maxclust")
    mbv_cons = df.groupby(consensus_labels)["MBV"].mean().sort_values(ascending=False)
    remap_cons = {old: new for new, old in enumerate(mbv_cons.index, start=1)}
    df["consensus_k5"] = consensus_labels
    df["consensus_ordered"] = df["consensus_k5"].map(remap_cons)

    ari = adjusted_rand_score(df["cluster_ordered"], df["consensus_ordered"])
    print(f"\nARI (cluster_ordered vs consensus_ordered): {ari:.4f}")

    scores = np.empty(n)
    for i in range(n):
        same_cluster = (df["cluster_ordered"] == df.iloc[i]["cluster_ordered"]).values
        scores[i] = consensus[i, same_cluster].mean()
    df["consensus_score"] = scores
    df["consensus_category"] = pd.cut(
        scores, bins=[0, 0.7, 0.8, 1.0001], labels=["Uncertain", "Ambiguous", "Stable"]
    )

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote: {OUTPUT_CSV.name}")
    print(f"Wrote: {CONSENSUS_NPY.name} (shape {consensus.shape})")
    print(f"Wrote: {INERTIA_NPY.name}")
    print("\nTypology counts (cluster_ordered):")
    print(df["cluster_ordered"].value_counts().sort_index().to_string())
    print("\nStability category:")
    print(df["consensus_category"].value_counts().to_string())


if __name__ == "__main__":
    main()
