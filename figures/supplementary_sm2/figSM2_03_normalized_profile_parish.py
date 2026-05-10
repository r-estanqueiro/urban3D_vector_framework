"""
Figure SM2_03 — Normalized structural profile by parish.

Coolwarm heatmap: rows = the three structural metrics (Mass / Heterogeneity /
Aperture), columns = parishes. Values are min-max normalized across parishes
per metric so that within-row colour comparisons are meaningful.

Output: figures/output/supplementary_sm2/Figure_SM2_03_Normalized_Profile_Parish.jpg
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

ROOT = Path(__file__).resolve().parents[2]
TYPOLOGY_CSV = ROOT / "SM2" / "output" / "BGRI_Final_Typology_k5_Production.csv"
OUT_DIR = ROOT / "figures" / "output" / "supplementary_sm2"
OUT_PATH = OUT_DIR / "Figure_SM2_03_Normalized_Profile_Parish.jpg"

DPI = 600
PARISH_COL = "DTMNFR21"
METRICS = ["MBV", "HVC", "svf_mean"]
PRETTY = ["Mass (MBV)", "Heterogeneity (HVC)", "Aperture (svf_mean)"]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TYPOLOGY_CSV).dropna(subset=METRICS + [PARISH_COL])
    parish_metrics = df.groupby(PARISH_COL)[METRICS].mean()

    scaler = MinMaxScaler()
    parish_metrics_norm = pd.DataFrame(
        scaler.fit_transform(parish_metrics),
        index=parish_metrics.index,
        columns=PRETTY,
    )

    plt.rcParams["figure.dpi"] = DPI
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        parish_metrics_norm.T, annot=True, fmt=".2f", cmap="coolwarm",
        cbar_kws={"label": "Normalized Value (0-1)"},
        linewidths=0.5, linecolor="white", vmin=0, vmax=1, ax=ax,
    )
    ax.set_title(
        "Structural Profile Aggregated by Parish (Normalized 0-1)",
        fontsize=14, fontweight="bold", pad=20,
    )
    ax.set_xlabel("Parish (DTMNFR21)", fontsize=12)
    ax.set_ylabel("Metric", fontsize=12)
    plt.xticks(rotation=0)
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=DPI, bbox_inches="tight", pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"wrote {OUT_PATH.name}")


if __name__ == "__main__":
    main()
