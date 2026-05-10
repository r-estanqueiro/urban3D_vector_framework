"""
Figure SM2_04 — Pie charts of typology composition per parish.

2x3 grid of pie charts, one per parish (DTMNFR21). Each pie shows the share of
the five typologies in that parish; viridis palette consistent with Figure 10.

Output: figures/output/supplementary_sm2/Figure_SM2_04_Pie_Charts_Composition_Parish.jpg
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import Normalize

ROOT = Path(__file__).resolve().parents[2]
TYPOLOGY_CSV = ROOT / "SM2" / "output" / "BGRI_Final_Typology_k5_Production.csv"
OUT_DIR = ROOT / "figures" / "output" / "supplementary_sm2"
OUT_PATH = OUT_DIR / "Figure_SM2_04_Pie_Charts_Composition_Parish.jpg"

DPI = 600
PARISH_COL = "DTMNFR21"
TYPES = [f"Type {i}" for i in range(1, 6)]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TYPOLOGY_CSV).dropna(subset=["cluster_ordered", PARISH_COL]).copy()
    df["cluster_ordered"] = df["cluster_ordered"].astype(int)
    df["Typology"] = df["cluster_ordered"].map(lambda i: f"Type {i}")

    cmap = plt.get_cmap("viridis")
    norm = Normalize(vmin=0, vmax=4)
    colors = [cmap(norm(i)) for i in range(5)]

    parishes = sorted(df[PARISH_COL].unique())

    plt.rcParams["figure.dpi"] = DPI
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for i, parish in enumerate(parishes):
        sub = df[df[PARISH_COL] == parish]
        counts = sub["Typology"].value_counts().reindex(TYPES, fill_value=0)
        pct = (counts / counts.sum() * 100).values
        axes[i].pie(counts, colors=colors, startangle=90,
                    wedgeprops={"linewidth": 2, "edgecolor": "white"})
        axes[i].set_title(f"Parish {parish}\n(n = {len(sub)} blocks)",
                          fontsize=12, fontweight="bold")
        labels = [f"{lab}: {p:.1f}%" for lab, p in zip(counts.index, pct)]
        axes[i].legend(labels, loc="center left", bbox_to_anchor=(1, 0.5),
                       fontsize=9, frameon=True)

    for j in range(len(parishes), 6):
        axes[j].axis("off")

    fig.suptitle("Typology Composition by Parish",
                 fontsize=16, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_PATH, dpi=DPI, bbox_inches="tight", pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"wrote {OUT_PATH.name}")


if __name__ == "__main__":
    main()
