# SM2 — Statistical Analysis & Typology Identification

K-Means clustering (k = 5) of urban blocks on the three SM1 metrics (MBV, HVC, svf_mean), validated by 500-iteration consensus clustering. Reports ARI ≈ 0.92–0.95 on Amadora's 816 valid blocks (the paper reports 0.9445; this build reports 0.9257 — see [Determinism](#determinism) for why).

---

## Inputs

`SM2/input/`:

- `BGRI_Complete_Metrics.csv` — output of SM1; required columns `BGRI2021`, `MBV`, `HVC`, `svf_mean`; optional `DTMNFR21` (parish code, used by Figure 10 and SM2 figures). **Provided** (canonical SM1 output is committed here so SM2 + figures can run without producing the SVF raster yourself).

## Outputs

Written to `SM2/output/` (gitignored — regenerable):

- `BGRI_Final_Typology_k5_Production.csv` — per-block typology assignment.
  - `cluster_ordered` — K-Means cluster ID, reordered 1..5 by descending mean MBV.
  - `consensus_ordered` — same reordering for the consensus partition.
  - `consensus_score` — per-block mean consensus value with same-cluster blocks (0–1).
  - `consensus_category` — `Stable` (≥ 0.8) · `Ambiguous` (0.7–0.8) · `Uncertain` (< 0.7).
  - `MBV_z`, `HVC_z`, `svf_mean_z` — standardised metrics (used by figures 06 and 08).
- `consensus_matrix_k5.npy` — 816×816 consensus matrix C; loaded by Figure 04.
- `inertia_k2_to_9.npy` — inertia values for k = 2..9; loaded by Figure 03.

## Determinism

The script seeds a single `numpy.random.default_rng(SEED=42)` for all consensus subsample draws; KMeans uses `random_state=42` for the canonical fit and `random_state=it` per consensus iteration. Re-running on the same input reproduces every output bit-for-bit on the same NumPy / scikit-learn versions.

**Why ARI is 0.9257 here vs. 0.9445 in the paper.** The paper run used the legacy global RNG (`np.random.choice` with no explicit seed), which is non-reproducible across machines. Switching to a seeded `default_rng` draws different (but deterministic) 80% subsamples → slightly different consensus matrix → slightly different consensus partition. The K-Means fit itself is identical, the typology counts are identical (24 / 231 / 93 / 299 / 169), and ARI = 0.9257 still indicates very high agreement. **Figure scripts MUST load the persisted CSV / NPY artifacts in this `output/`** — they must not re-run K-Means or consensus, or the figures will drift from the persisted typology assignment.

## Running

From `final/` with the venv active:

```powershell
.\.venv\Scripts\Activate.ps1
cd SM2
python SM2_Code_Typology_Consensus.py
```

Expected runtime: 1–3 minutes (the 500-iteration consensus loop dominates).

Dependencies are installed once via `pip install -e ".[sm1,sm2,figures,test]"` against the project's `pyproject.toml`. The `[sm2]` extra alone covers SM2: `pandas`, `numpy`, `scikit-learn`, `scipy`.

## Workflow

1. Drop NaN in MBV/HVC/svf_mean (816 of 822 rows survive).
2. `StandardScaler` → z-scores.
3. Pearson correlation + PCA (diagnostic).
4. Elbow method, k = 2..9.
5. K-Means (k = 5, n_init = 20, random_state = 42); reorder by descending mean MBV.
6. Consensus clustering: 500 iterations × 80% subsampling × KMeans → co-occurrence / counts → consensus matrix C.
7. Average-linkage hierarchical clustering on `1 - C`; cut to 5 partitions; reorder by MBV.
8. Per-block consensus score + 'Stable' / 'Ambiguous' / 'Uncertain' category.

## Typologies (after MBV-descending reorder)

| Type | Block count | Profile |
|---|---:|---|
| 1 | 24 | Very High Volume, Low-Heterogeneity |
| 2 | 231 | High Volume, Low-Heterogeneity Compact |
| 3 | 93 | High Volume, High-Heterogeneity |
| 4 | 299 | Low Volume, Mixed-Height |
| 5 | 169 | Low Volume, High-Aperture |

(Counts are deterministic with `SEED=42`.)

## Authors & license

**Software author** (this code): Rossana Estanqueiro.

**Manuscript authors** (accompanying paper, submitted):
**Rossana Estanqueiro¹,²,\*, Carla Rebelo², José António Tenedório¹,²**

¹ Universidade NOVA de Lisboa, Faculty of Social Sciences and Humanities, Department of Geography and Regional Planning, Avenida de Berna 26-C, 1069-061 Lisbon, Portugal
² Centre for Functional Ecology—Science for People & the Planet (CFE), University of Coimbra, History, Territories and Communities, Faculty of Social Sciences and Humanities (NOVA FCSH), Universidade NOVA de Lisboa, Associate Laboratory TERRA, Avenida de Berna 26-C, 1069-061 Lisbon, Portugal

\* Contact: rossana.estanqueiro@fcsh.unl.pt

## Acknowledgements

The authors thank **Francisco Pires** for his support with the Python implementation.

License: MIT
