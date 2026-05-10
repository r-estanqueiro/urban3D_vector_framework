"""
Figure 06 — Radar profiles of the five typologies.

Five small-multiple polar plots (a)..(e), one per typology, each showing the
mean of the standardised metrics MBV_z, HVC_z, SVF_z. Values are min-max
normalised across typologies for visual comparability; raw means are annotated
on each axis. The 6th panel of the 2x3 grid is hidden.

Output: figures/output/article/Figure_06_Radar_Profiles_Five_Typologies.jpg
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TYPOLOGY_CSV = ROOT / "SM2" / "output" / "BGRI_Final_Typology_k5_Production.csv"
OUT_DIR = ROOT / "figures" / "output" / "article"
OUT_PATH = OUT_DIR / "Figure_06_Radar_Profiles_Five_Typologies.jpg"

DPI = 600
METRICS = ["MBV_z", "HVC_z", "svf_mean_z"]
LABELS = ["MBV$_z$\n(Mean Building\nVolume)",
          "HVC$_z$\n(Height Variation\nCoefficient)",
          "SVF$_z$\n(Sky View\nFactor)"]
COLORS = ["#440154", "#21908C", "#CC8800", "#3B528B", "#5DC863"]
PANEL_LABELS = ["(a)", "(b)", "(c)", "(d)", "(e)"]


def close_loop(arr):
    return np.append(arr, arr[0])


def draw_radar(ax, norm_vals, raw_vals, color, angles):
    angles_closed = np.append(angles, angles[0])
    v = close_loop(norm_vals)
    ax.plot(angles_closed, v, color=color, linewidth=3.0, zorder=3)
    ax.fill(angles_closed, v, color=color, alpha=0.28, zorder=2)
    ax.scatter(angles, norm_vals, s=55, color=color, zorder=4,
               edgecolors="white", linewidth=1.0)
    for ang, nv, rv in zip(angles, norm_vals, raw_vals):
        r_label = min(nv + 0.22, 1.30)
        ax.annotate(
            f"{rv:+.2f}",
            xy=(ang, r_label),
            fontsize=9, color="black", fontweight="bold",
            ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.18", fc="white",
                      ec=color, alpha=0.88, linewidth=0.9),
        )


def style_radar(ax, angles):
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles)
    ax.set_xticklabels(LABELS, fontsize=9, fontweight="bold",
                       color="black", linespacing=1.3)
    ax.tick_params(axis="x", pad=14)
    ax.set_ylim(0, 1.45)
    ax.set_yticks([0.25, 0.50, 0.75, 1.00])
    ax.set_yticklabels([])
    ax.yaxis.grid(True, color="grey", alpha=0.40, linewidth=0.7, linestyle="--")
    ax.xaxis.grid(True, color="grey", alpha=0.40, linewidth=0.7)
    ax.spines["polar"].set_color("grey")
    ax.spines["polar"].set_linewidth(0.6)
    ax.set_facecolor("#F8F8F8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TYPOLOGY_CSV).dropna(subset=METRICS + ["cluster_ordered"]).copy()
    df["cluster_ordered"] = df["cluster_ordered"].astype(int)
    types = sorted(df["cluster_ordered"].unique())

    stats = {}
    for t in types:
        sub = df.loc[df["cluster_ordered"] == t, METRICS]
        stats[t] = {"n": len(sub), "mean": sub.mean().values, "std": sub.std().values}

    all_means = np.array([stats[t]["mean"] for t in types])
    metric_min = all_means.min(axis=0)
    metric_range = all_means.max(axis=0) - metric_min
    metric_range[metric_range == 0] = 1.0
    for t in types:
        stats[t]["norm"] = (stats[t]["mean"] - metric_min) / metric_range

    angles = np.linspace(0, 2 * np.pi, len(METRICS), endpoint=False)

    plt.rcParams["figure.dpi"] = DPI
    fig, axes = plt.subplots(2, 3, figsize=(18, 13), subplot_kw=dict(polar=True))
    axes_flat = axes.flatten()
    axes_flat[5].set_visible(False)

    for idx, t in enumerate(types):
        ax = axes_flat[idx]
        color = COLORS[t - 1]
        draw_radar(ax, stats[t]["norm"], stats[t]["mean"], color, angles)
        style_radar(ax, angles)
        ax.set_title(f"{PANEL_LABELS[idx]}  Type {t}   (n = {stats[t]['n']})",
                     fontsize=14, fontweight="bold", color=color, pad=20)
        metric_strs = [
            f"MBV$_z$ = {stats[t]['mean'][0]:+.3f} ± {stats[t]['std'][0]:.3f}",
            f"HVC$_z$ = {stats[t]['mean'][1]:+.3f} ± {stats[t]['std'][1]:.3f}",
            f"SVF$_z$ = {stats[t]['mean'][2]:+.3f} ± {stats[t]['std'][2]:.3f}",
        ]
        ax.text(0, -0.30, "\n".join(metric_strs),
                transform=ax.transAxes, ha="center", va="top",
                fontsize=11, color="#111111",
                bbox=dict(boxstyle="round,pad=0.6", fc="white",
                          ec=color, alpha=0.92, linewidth=1.2))

    fig.tight_layout(pad=3.0, h_pad=5.0, w_pad=3.0)
    fig.savefig(OUT_PATH, dpi=DPI, bbox_inches="tight", facecolor="white", pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"wrote {OUT_PATH.name}")


if __name__ == "__main__":
    main()
