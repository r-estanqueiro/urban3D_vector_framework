"""
Figure 03 — Elbow method, optimal k.

Loads the persisted inertia values from SM2 (`SM2/output/inertia_k2_to_9.npy`)
and plots inertia vs. k for k = 2..9. The elbow at k = 5 motivates the
five-typology partition used throughout the paper.

Output: figures/output/article/Figure_03_Elbow_Method_Optimal_K.jpg
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
INERTIA_NPY = ROOT / "SM2" / "output" / "inertia_k2_to_9.npy"
OUT_DIR = ROOT / "figures" / "output" / "article"
OUT_PATH = OUT_DIR / "Figure_03_Elbow_Method_Optimal_K.jpg"

DPI = 600


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inertia = np.load(INERTIA_NPY)
    k_range = np.arange(2, 2 + len(inertia))

    plt.rcParams["figure.dpi"] = DPI
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(k_range, inertia, "o-", color="steelblue", linewidth=2, markersize=6)
    ax.set_xlabel("Number of clusters (k)", fontsize=11)
    ax.set_ylabel("Inertia (within-cluster sum of squares)", fontsize=11)
    ax.set_title("Elbow Method for Optimal k", fontsize=12, fontweight="bold")
    ax.set_xticks(k_range)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=DPI, bbox_inches="tight", pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"wrote {OUT_PATH.name}")


if __name__ == "__main__":
    main()
