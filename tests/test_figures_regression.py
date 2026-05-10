"""Figure regression tests.

For each figure: assert the file exists, has a sensible byte size (catches
'empty figure' regressions), and has dimensions consistent with the source
script's `figsize * 600 dpi` setting. No pixel-perfect comparison — matplotlib
version drift would break it, and the consensus matrix's seeded RNG already
moves a few pixels around (see SM2 README).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ARTICLE_OUT = ROOT / "figures" / "output" / "article"
SM2_OUT = ROOT / "figures" / "output" / "supplementary_sm2"

# All figures are 600 DPI JPEG (quality=95) per the publication requirement.
# (filename, min KB, max KB, min width px, min height px)
EXPECTED = [
    # article
    (ARTICLE_OUT / "Figure_03_Elbow_Method_Optimal_K.jpg",             20,  1_000, 2000, 1500),
    (ARTICLE_OUT / "Figure_04_Consensus_Matrix_k5.jpg",               200, 10_000, 4000, 3000),
    (ARTICLE_OUT / "Figure_05_Kmeans_vs_Consensus_Agreement.jpg",      30,  1_500, 3000, 3000),
    (ARTICLE_OUT / "Figure_06_Radar_Profiles_Five_Typologies.jpg",    200,  4_000, 7000, 5000),
    (ARTICLE_OUT / "Figure_07_Boxplots_Structural_Metrics.jpg",        50,  1_500, 6000, 1500),
    (ARTICLE_OUT / "Figure_08_Pairwise_Scatter_Standardized.jpg",     200,  4_000, 4000, 4000),
    (ARTICLE_OUT / "Figure_10_Typologies_by_Parish.jpg",              100,  3_000, 5000, 2500),
    # SM2
    (SM2_OUT / "Figure_SM2_01_Heatmap_Typology_Frequency_Parish.jpg",  80, 2_000, 3500, 2000),
    (SM2_OUT / "Figure_SM2_02_Heatmap_Block_Count_Parish.jpg",         80, 2_000, 3500, 2000),
    (SM2_OUT / "Figure_SM2_03_Normalized_Profile_Parish.jpg",          50, 2_000, 3000, 2000),
    (SM2_OUT / "Figure_SM2_04_Pie_Charts_Composition_Parish.jpg",     200, 4_000, 6000, 4000),
]


@pytest.mark.parametrize(
    "path,min_kb,max_kb,min_w,min_h",
    EXPECTED,
    ids=[p[0].name for p in EXPECTED],
)
def test_figure_artifact(sm2_outputs_ready, path, min_kb, max_kb, min_w, min_h):
    """Each figure file exists, has a plausible size, and plausible dimensions."""
    # The figure script smoke test (test_smoke) is what actually generates the files.
    # If pytest runs only this module, generate them on demand.
    if not path.exists():
        import subprocess, sys
        # Map output path back to its source script.
        if path.parent == ARTICLE_OUT:
            src_dir = ROOT / "figures" / "article"
            stem_map = {
                "Figure_03_Elbow_Method_Optimal_K.jpg":            "fig03_elbow.py",
                "Figure_04_Consensus_Matrix_k5.jpg":               "fig04_consensus_matrix.py",
                "Figure_05_Kmeans_vs_Consensus_Agreement.jpg":     "fig05_kmeans_vs_consensus.py",
                "Figure_06_Radar_Profiles_Five_Typologies.jpg":    "fig06_radar_profiles.py",
                "Figure_07_Boxplots_Structural_Metrics.jpg":       "fig07_boxplots.py",
                "Figure_08_Pairwise_Scatter_Standardized.jpg":     "fig08_pairwise_scatter.py",
                "Figure_10_Typologies_by_Parish.jpg":              "fig10_typologies_by_parish.py",
            }
        else:
            src_dir = ROOT / "figures" / "supplementary_sm2"
            stem_map = {
                "Figure_SM2_01_Heatmap_Typology_Frequency_Parish.jpg": "figSM2_01_heatmap_freq_parish.py",
                "Figure_SM2_02_Heatmap_Block_Count_Parish.jpg":        "figSM2_02_heatmap_counts_parish.py",
                "Figure_SM2_03_Normalized_Profile_Parish.jpg":         "figSM2_03_normalized_profile_parish.py",
                "Figure_SM2_04_Pie_Charts_Composition_Parish.jpg":     "figSM2_04_pie_charts_parish.py",
            }
        script = src_dir / stem_map[path.name]
        subprocess.run([sys.executable, str(script)], check=True, timeout=300)

    assert path.exists(), f"missing figure: {path}"

    size_kb = path.stat().st_size / 1024
    assert min_kb <= size_kb <= max_kb, (
        f"{path.name}: size {size_kb:.1f} KB outside [{min_kb}, {max_kb}] KB band"
    )

    with Image.open(path) as im:
        w, h = im.size
    assert w >= min_w, f"{path.name}: width {w} < {min_w}"
    assert h >= min_h, f"{path.name}: height {h} < {min_h}"
