"""
Figure SM2_02 — Heatmap of absolute block counts by parish and typology.

YlOrRd heatmap: rows = parishes (DTMNFR21), columns = typologies, cells = block
count. Complement to Figure SM2_01 (which shows percentages).

Output: figures/output/supplementary_sm2/Figure_SM2_02_Heatmap_Block_Count_Parish.jpg
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[2]
TYPOLOGY_CSV = ROOT / "SM2" / "output" / "BGRI_Final_Typology_k5_Production.csv"
OUT_DIR = ROOT / "figures" / "output" / "supplementary_sm2"
OUT_PATH = OUT_DIR / "Figure_SM2_02_Heatmap_Block_Count_Parish.jpg"

DPI = 600
PARISH_COL = "DTMNFR21"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TYPOLOGY_CSV).dropna(subset=["cluster_ordered", PARISH_COL]).copy()
    df["cluster_ordered"] = df["cluster_ordered"].astype(int)
    df["Typology"] = df["cluster_ordered"].map(lambda i: f"Type {i}")

    counts = pd.crosstab(df[PARISH_COL], df["Typology"])
    counts = counts[[f"Type {i}" for i in range(1, 6)]]

    plt.rcParams["figure.dpi"] = DPI
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        counts, annot=True, fmt="d", cmap="YlOrRd",
        cbar_kws={"label": "Number of Blocks"},
        linewidths=0.5, linecolor="white", ax=ax,
    )
    ax.set_title(
        "Distribution of Typologies by Parish (BGRI Blocks Count)",
        fontsize=14, fontweight="bold", pad=20,
    )
    ax.set_xlabel("Typology", fontsize=12)
    ax.set_ylabel("Parish (DTMNFR21)", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=DPI, bbox_inches="tight", pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"wrote {OUT_PATH.name}")


if __name__ == "__main__":
    main()
