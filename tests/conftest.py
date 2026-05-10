"""Shared pytest fixtures for SM1/SM2/figure regression tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SM1_DIR = ROOT / "SM1"
SM2_DIR = ROOT / "SM2"
FIG_DIR = ROOT / "figures"

SM2_OUTPUTS = [
    SM2_DIR / "output" / "BGRI_Final_Typology_k5_Production.csv",
    SM2_DIR / "output" / "consensus_matrix_k5.npy",
    SM2_DIR / "output" / "inertia_k2_to_9.npy",
]


@pytest.fixture(scope="session")
def project_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def sm2_outputs_ready() -> dict[str, Path]:
    """Ensure SM2 has been run; populate output/ if missing.

    Runs SM2 once per test session. Subsequent tests share the artifacts.
    """
    if not all(p.exists() for p in SM2_OUTPUTS):
        result = subprocess.run(
            [sys.executable, str(SM2_DIR / "SM2_Code_Typology_Consensus.py")],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            pytest.fail(f"SM2 setup run failed:\n{result.stdout}\n{result.stderr}")
    for p in SM2_OUTPUTS:
        assert p.exists(), f"missing SM2 output: {p}"
    return {p.name: p for p in SM2_OUTPUTS}


@pytest.fixture(scope="session")
def svf_available() -> bool:
    return (SM1_DIR / "input" / "svf.tif").exists()
