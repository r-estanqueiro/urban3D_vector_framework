"""
Figure 08 — Pairwise scatter matrix of standardised metrics.

3x3 panel matrix: KDE per typology on the diagonal, scatter (lower triangle)
of MBV_z vs HVC_z vs SVF_z, colour-coded by typology. Smaller clusters are
plotted on top so they remain visible.

Output: figures/output/article/Figure_08_Pairwise_Scatter_Standardized.jpg
"""

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

ROOT = Path(__file__).resolve().parents[2]
TYPOLOGY_CSV = ROOT / "SM2" / "output" / "BGRI_Final_Typology_k5_Production.csv"
OUT_DIR = ROOT / "figures" / "output" / "article"
OUT_PATH = OUT_DIR / "Figure_08_Pairwise_Scatter_Standardized.jpg"

DPI = 600
DIMS = ["MBV_z", "HVC_z", "svf_mean_z"]
LABELS = {"MBV_z": r"MBV$_z$", "HVC_z": r"HVC$_z$", "svf_mean_z": r"SVF$_z$"}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TYPOLOGY_CSV).dropna(subset=["MBV", "HVC", "svf_mean"]).reset_index(drop=True)
    df["cluster_ordered"] = df["cluster_ordered"].astype(int)

    viridis = plt.cm.viridis(np.linspace(0, 0.95, 5))
    plot_order = (
        df["cluster_ordered"].value_counts().sort_values(ascending=False).index.tolist()
    )
    limits = {d: (df[d].min() - 0.3, df[d].max() + 0.3) for d in DIMS}

    plt.rcParams["figure.dpi"] = DPI
    fig, axes = plt.subplots(3, 3, figsize=(11, 10))

    for i, dim_y in enumerate(DIMS):
        for j, dim_x in enumerate(DIMS):
            ax = axes[i, j]
            if i == j:
                x_range = np.linspace(*limits[dim_x], 200)
                for t in [1, 2, 3, 4, 5]:
                    sub = df.loc[df["cluster_ordered"] == t, dim_x].values
                    if len(sub) > 1:
                        kde = gaussian_kde(sub)
                        ax.plot(x_range, kde(x_range), color=viridis[t - 1], linewidth=1.8)
                        ax.fill_between(x_range, kde(x_range), color=viridis[t - 1], alpha=0.12)
                ax.set_yticks([])
                ax.set_xlim(*limits[dim_x])
            elif i > j:
                for t in plot_order:
                    sub = df[df["cluster_ordered"] == t]
                    edge = "black" if t == 1 else "none"
                    lw = 0.3 if t == 1 else 0
                    ax.scatter(sub[dim_x], sub[dim_y],
                               c=[viridis[t - 1]], s=14, alpha=0.55,
                               edgecolors=edge, linewidths=lw)
                ax.axhline(0, color="gray", linewidth=0.4, alpha=0.6)
                ax.axvline(0, color="gray", linewidth=0.4, alpha=0.6)
                ax.set_xlim(*limits[dim_x])
                ax.set_ylim(*limits[dim_y])
            else:
                ax.set_visible(False)

            if i == 2:
                ax.set_xlabel(LABELS[dim_x], fontsize=13, fontweight="bold")
            if j == 0:
                ax.set_ylabel(LABELS[dim_y], fontsize=13, fontweight="bold")
            ax.tick_params(axis="both", labelsize=9)

    handles = [
        mpatches.Patch(
            color=viridis[i],
            label=f"Type {i+1} (n = {(df['cluster_ordered'] == i+1).sum()})",
        )
        for i in range(5)
    ]
    fig.legend(
        handles=handles, loc="upper right", bbox_to_anchor=(0.93, 0.93),
        fontsize=10, frameon=True, framealpha=0.92, edgecolor="gray",
        title="Urban Block Typology", title_fontsize=11,
    )
    fig.suptitle(
        f"Pairwise distribution of structural metrics across the {len(df)} urban blocks",
        fontsize=12, fontweight="bold", y=0.97,
    )
    fig.tight_layout(rect=[0.02, 0.02, 0.98, 0.95])
    fig.savefig(OUT_PATH, dpi=DPI, bbox_inches="tight", facecolor="white", pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"wrote {OUT_PATH.name}")


if __name__ == "__main__":
    main()
