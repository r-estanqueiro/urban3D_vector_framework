"""Smoke tests: every pipeline + figure script runs to completion without raising.

SM1 is skipped when the SVF raster isn't present (it's intentionally not shipped
with the repo). SM2 + every figure script must always pass.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SM1_SCRIPT = ROOT / "SM1" / "SM1_Code_3D_Metrics.py"
SM2_SCRIPT = ROOT / "SM2" / "SM2_Code_Typology_Consensus.py"

ARTICLE_FIGS = sorted((ROOT / "figures" / "article").glob("fig*.py"))
SM2_FIGS = sorted((ROOT / "figures" / "supplementary_sm2").glob("figSM2_*.py"))
ALL_FIGS = ARTICLE_FIGS + SM2_FIGS


def _run(script: Path, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_sm1_runs_or_reports_missing_svf(svf_available):
    """SM1 either runs to completion (if SVF present) or exits non-zero with a clear hint."""
    result = _run(SM1_SCRIPT, timeout=900)
    if svf_available:
        assert result.returncode == 0, (
            f"SM1 failed with SVF present:\nSTDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )
    else:
        assert result.returncode != 0, "SM1 should exit non-zero when svf.tif is missing"
        assert "svf.tif" in result.stdout or "svf.tif" in result.stderr


def test_sm2_runs(sm2_outputs_ready):
    """sm2_outputs_ready fixture itself runs SM2 if needed; this test just confirms artifacts."""
    assert all(p.exists() for p in sm2_outputs_ready.values())


@pytest.mark.parametrize("script", ALL_FIGS, ids=lambda p: p.name)
def test_figure_script_runs(script, sm2_outputs_ready):
    """Each figure script must run end-to-end without raising."""
    result = _run(script, timeout=300)
    assert result.returncode == 0, (
        f"{script.name} failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
