"""
Figure 10 — Distribution of typologies by parish (relative frequency).

Stacked bar chart, viridis palette, one bar per parish (DTMNFR21). Bars sum to
100% so the parish-by-parish typology mix is directly comparable.

Output: figures/output/article/Figure_10_Typologies_by_Parish.jpg
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import Normalize

ROOT = Path(__file__).resolve().parents[2]
TYPOLOGY_CSV = ROOT / "SM2" / "output" / "BGRI_Final_Typology_k5_Production.csv"
OUT_DIR = ROOT / "figures" / "output" / "article"
OUT_PATH = OUT_DIR / "Figure_10_Typologies_by_Parish.jpg"

DPI = 600
PARISH_COL = "DTMNFR21"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TYPOLOGY_CSV).dropna(subset=["cluster_ordered", PARISH_COL]).copy()
    df["cluster_ordered"] = df["cluster_ordered"].astype(int)
    df["Typology"] = df["cluster_ordered"].map(lambda i: f"Type {i}")

    cmap = plt.get_cmap("viridis")
    norm = Normalize(vmin=0, vmax=4)
    colors = [cmap(norm(i)) for i in range(5)]

    counts = pd.crosstab(df[PARISH_COL], df["Typology"])
    counts = counts[[f"Type {i}" for i in range(1, 6)]]
    freq = counts.div(counts.sum(axis=1), axis=0) * 100

    plt.rcParams["figure.dpi"] = DPI
    fig, ax = plt.subplots(figsize=(14, 7))
    freq.plot(kind="bar", stacked=True, ax=ax, color=colors,
              edgecolor="white", linewidth=1.5, width=0.7)
    ax.set_title("Distribution of Typologies by Parish (Relative Frequency)",
                 fontsize=15, fontweight="bold", pad=20)
    ax.set_xlabel("Parish (DTMNFR21)", fontsize=13)
    ax.set_ylabel("Percentage of Blocks (%)", fontsize=13)
    ax.legend(title="Typology", bbox_to_anchor=(1.02, 1), loc="upper left",
              frameon=True, fontsize=11)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=11)
    ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=DPI, bbox_inches="tight", pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"wrote {OUT_PATH.name}")


if __name__ == "__main__":
    main()
