"""
Figure 05 — K-Means vs. Consensus agreement.

Confusion matrix (5 x 5) of K-Means typology (rows) against consensus typology
(columns) for the 816 blocks. The Adjusted Rand Index is annotated.

Output: figures/output/article/Figure_05_Kmeans_vs_Consensus_Agreement.jpg
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import adjusted_rand_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[2]
TYPOLOGY_CSV = ROOT / "SM2" / "output" / "BGRI_Final_Typology_k5_Production.csv"
OUT_DIR = ROOT / "figures" / "output" / "article"
OUT_PATH = OUT_DIR / "Figure_05_Kmeans_vs_Consensus_Agreement.jpg"

DPI = 600


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TYPOLOGY_CSV)
    cm = confusion_matrix(df["cluster_ordered"], df["consensus_ordered"])
    ari = adjusted_rand_score(df["cluster_ordered"], df["consensus_ordered"])

    plt.rcParams["figure.dpi"] = DPI
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar_kws={"label": "Number of blocks"},
        xticklabels=[f"Type {i}" for i in range(1, 6)],
        yticklabels=[f"Type {i}" for i in range(1, 6)],
        square=True,
        linewidths=0.5,
        linecolor="gray",
        ax=ax,
    )
    ax.set_xlabel("Consensus Typology", fontsize=12, fontweight="bold")
    ax.set_ylabel("K-Means Typology", fontsize=12, fontweight="bold")
    ax.set_title(f"Agreement: K-Means vs Consensus (ARI = {ari:.3f})",
                 fontsize=14, fontweight="bold", pad=15)
    ax.text(0.5, -0.15, f"Adjusted Rand Index: {ari:.4f}",
            transform=ax.transAxes, ha="center", fontsize=11,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=DPI, bbox_inches="tight", pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"wrote {OUT_PATH.name}  (ARI = {ari:.4f})")


if __name__ == "__main__":
    main()
