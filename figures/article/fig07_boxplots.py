"""
Figure 07 — Boxplots of structural metrics by typology.

Three side-by-side panels named after the three structural dimensions of the
geometric vector framework (Section 2.2 of the article):
  (a) Mass Dimension          — Mean Building Volume (m^3)
  (b) Heterogeneity Dimension — Height Variation Coefficient (dimensionless)
  (c) Aperture Dimension      — Mean Sky View Factor (0-1)
Box = 25th-75th percentile, whiskers = 1.5 x IQR, points beyond = outliers.

Output: figures/output/article/Figure_07_Boxplots_Structural_Metrics.jpg
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[2]
TYPOLOGY_CSV = ROOT / "SM2" / "output" / "BGRI_Final_Typology_k5_Production.csv"
OUT_DIR = ROOT / "figures" / "output" / "article"
OUT_PATH = OUT_DIR / "Figure_07_Boxplots_Structural_Metrics.jpg"

DPI = 600
METRICS = ["MBV", "HVC", "svf_mean"]
PANEL_TITLES = [
    "(a) Mass Dimension",
    "(b) Heterogeneity Dimension",
    "(c) Aperture Dimension",
]
Y_LABELS = [
    "Mean Building Volume (m³)",
    "Height Variation Coefficient",
    "Mean Sky View Factor",
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TYPOLOGY_CSV).dropna(subset=METRICS + ["cluster_ordered"])

    plt.rcParams["figure.dpi"] = DPI
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for i, (metric, panel_title, ylabel) in enumerate(zip(METRICS, PANEL_TITLES, Y_LABELS)):
        sns.boxplot(
            data=df,
            x="cluster_ordered",
            y=metric,
            hue="cluster_ordered",
            palette="viridis",
            legend=False,
            ax=axes[i],
        )
        axes[i].set_xlabel("Typology", fontsize=10)
        axes[i].set_ylabel(ylabel, fontsize=10)
        axes[i].set_title(panel_title, fontsize=11, fontweight="bold")
        ticks = axes[i].get_xticks()
        axes[i].set_xticks(ticks)
        axes[i].set_xticklabels([f"T{i + 1}" for i in range(len(ticks))])
        axes[i].grid(True, alpha=0.3)

    fig.suptitle("3D Structural Metrics by Typology", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=DPI, bbox_inches="tight", pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"wrote {OUT_PATH.name}")


if __name__ == "__main__":
    main()
