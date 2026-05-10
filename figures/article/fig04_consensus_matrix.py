"""
Figure 04 — Consensus matrix (k = 5, 500 iterations).

Loads `consensus_matrix_k5.npy` from SM2/output and reorders rows / columns by
the consensus typology so blocks of the same type cluster on the diagonal.
Green diagonal blocks indicate persistent co-assignment across the 500 K-Means
runs; red off-diagonal cells indicate persistent separation.

Output: figures/output/article/Figure_04_Consensus_Matrix_k5.jpg
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[2]
TYPOLOGY_CSV = ROOT / "SM2" / "output" / "BGRI_Final_Typology_k5_Production.csv"
CONSENSUS_NPY = ROOT / "SM2" / "output" / "consensus_matrix_k5.npy"
OUT_DIR = ROOT / "figures" / "output" / "article"
OUT_PATH = OUT_DIR / "Figure_04_Consensus_Matrix_k5.jpg"

DPI = 600


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TYPOLOGY_CSV)
    consensus = np.load(CONSENSUS_NPY)

    sort_idx = df.sort_values("consensus_ordered").index.values
    C_sorted = consensus[np.ix_(sort_idx, sort_idx)]

    plt.rcParams["figure.dpi"] = DPI
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        C_sorted,
        cmap="RdYlGn",
        vmin=0,
        vmax=1,
        cbar_kws={"label": "Consensus strength"},
        xticklabels=False,
        yticklabels=False,
        square=True,
        ax=ax,
    )

    typology_counts = (
        df.sort_values("consensus_ordered").groupby("consensus_ordered").size()
    )
    boundaries = np.cumsum(typology_counts.values)
    for b in boundaries[:-1]:
        ax.axhline(b, color="black", linewidth=1.5)
        ax.axvline(b, color="black", linewidth=1.5)

    n = len(df)
    positions = np.concatenate([[0], boundaries])
    centers = [(positions[i] + positions[i + 1]) / 2 for i in range(5)]
    for i, c in enumerate(centers):
        ax.text(-30, c, f"Type {i + 1}", va="center", ha="right",
                fontsize=11, fontweight="bold")
        ax.text(c, n + 30, f"Type {i + 1}", ha="center", va="top",
                fontsize=11, fontweight="bold")

    ax.set_xlabel("Blocks (ordered by consensus typology)",
                  fontsize=12, fontweight="bold")
    ax.set_ylabel("Blocks (ordered by consensus typology)",
                  fontsize=12, fontweight="bold")
    ax.set_title("Consensus Matrix (k=5, 500 iterations)",
                 fontsize=14, fontweight="bold", pad=20)
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=DPI, bbox_inches="tight", pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"wrote {OUT_PATH.name}")


if __name__ == "__main__":
    main()
