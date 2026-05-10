# urban3D_vector_framework

Reproducible Python pipeline accompanying the paper:

> **3D Urban Structural Morphology at the Block Scale: A Geometric Vector Framework Based on Mean Building Volume, Height Variation Coefficient, and Mean Sky View Factor**
> Rossana Estanqueiro, Carla Rebelo, José António Tenedório
> *(submitted)*

The pipeline characterises every urban block in Amadora, Portugal by three near-orthogonal 3D structural metrics — **MBV** (Mean Building Volume), **HVC** (Height Variation Coefficient), **SVF** (Mean Sky View Factor) — and derives five robust block typologies via K-Means (k = 5) validated by 500-iteration consensus clustering.

---

## Repo layout

```
urban3D_vector_framework/
├── LICENSE
├── README.md          ← this file
├── pyproject.toml     ← single source of truth for Python deps
├── SM1/               Supplementary Material 1 — geometric metrics
│   ├── SM1_README.md
│   ├── SM1_Code_3D_Metrics.py
│   ├── input/         buildings.shp, blocks.shp (provided); svf.tif (user-generated)
│   └── output/        Block_Complete_Metrics.shp + BGRI_Complete_Metrics.csv
├── SM2/               Supplementary Material 2 — clustering + consensus
│   ├── SM2_README.md
│   ├── SM2_Code_Typology_Consensus.py
│   ├── input/         BGRI_Complete_Metrics.csv (committed: SM1→SM2 handoff)
│   └── output/        BGRI_Final_Typology_k5_Production.csv + consensus_matrix_k5.npy + inertia_k2_to_9.npy
├── figures/           Per-figure scripts (one image each, 600 DPI)
│   ├── README.md
│   ├── article/                fig03..fig10 (Figs 3, 4, 5, 6, 7, 8, 10)
│   ├── supplementary_sm2/      figSM2_01..04 (parish-level analysis)
│   └── output/                 article/, supplementary_sm2/  (generated)
└── tests/
    ├── test_smoke.py
    └── test_figures_regression.py
```

`SM1/output/`, `SM2/output/`, `figures/output/` and `.venv/` are gitignored — every output is regenerable from the committed inputs (modulo the user-generated SVF raster, which only affects SM1).

## Quickstart

```powershell
# 1. Create virtual environment + install deps from pyproject.toml
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[sm1,sm2,figures,test]"

# 2. Run the typology pipeline (uses the committed BGRI_Complete_Metrics.csv)
cd SM2; python SM2_Code_Typology_Consensus.py; cd ..

# 3. Regenerate every figure (600 DPI)
Get-ChildItem figures\article\*.py, figures\supplementary_sm2\*.py |
  ForEach-Object { python $_.FullName }

# 4. Run the test suite
pytest
```

For Linux / macOS, replace `.\.venv\Scripts\Activate.ps1` with `source .venv/bin/activate` and the PowerShell pipeline in step 3 with a shell loop.

## Pipeline

```
   buildings.shp + blocks.shp + svf.tif
              │
              ▼   SM1/SM1_Code_3D_Metrics.py
   SM1/output/BGRI_Complete_Metrics.csv  ───► copied into  SM2/input/
              │                                      │
              │                                      ▼
              │                          SM2/SM2_Code_Typology_Consensus.py
              │                                      │
              │                                      ▼
              │                  SM2/output/BGRI_Final_Typology_k5_Production.csv
              │                  SM2/output/consensus_matrix_k5.npy
              │                  SM2/output/inertia_k2_to_9.npy
              │                                      │
              │                                      ▼
              │                          figures/{article,supplementary_sm2}/*.py
              │                                      │
              │                                      ▼
              │                          figures/output/.../Figure_*.{png,jpg}
```

The pipeline is **strict**: figure scripts only LOAD the persisted SM2 artifacts. They never re-run K-Means or consensus. The 500-iteration consensus runs once in SM2 with seeded RNG (`numpy.random.default_rng(42)`); its result is persisted as `consensus_matrix_k5.npy` and consumed by Figure 04. This guarantees the figures match the typology assignment in `BGRI_Final_Typology_k5_Production.csv` exactly.

## How to skip SM1

The 1.9 GB SVF raster needed by SM1 is generated externally (QGIS + SAGA — see [`SM1/SM1_README.md`](SM1/SM1_README.md)) and not distributed with this repo. If you only want to reproduce the typology + figures, skip SM1 entirely: the canonical SM1 output is committed at [`SM2/input/BGRI_Complete_Metrics.csv`](SM2/input/BGRI_Complete_Metrics.csv), so SM2 + every figure script run as-is.

## Outputs reference

| File | What | Produced by |
|---|---|---|
| `SM1/output/Block_Complete_Metrics.shp` | Block geometries with MBV, HVC, svf_mean | SM1 |
| `SM1/output/BGRI_Complete_Metrics.csv` | Tabular form of the above | SM1 |
| `SM2/output/BGRI_Final_Typology_k5_Production.csv` | Per-block typology (`cluster_ordered`, `consensus_ordered`, `consensus_score`, `consensus_category`, `*_z` metrics) | SM2 |
| `SM2/output/consensus_matrix_k5.npy` | 816×816 consensus matrix | SM2 |
| `SM2/output/inertia_k2_to_9.npy` | Elbow-method inertia values | SM2 |
| `figures/output/article/Figure_03..10.jpg` | 7 main-article figures (JPEG, 600 DPI, quality 95) | figures/article/ |
| `figures/output/supplementary_sm2/Figure_SM2_01..04.jpg` | 4 supplementary parish-level figures (JPEG, 600 DPI, quality 95) | figures/supplementary_sm2/ |

Figures 1, 2, 9 of the main article (study area map, methodology flowchart, spatial distribution map) are GIS / vector compositions and are not regenerated by code in this repo.

## Reproducibility & determinism

- **Python 3.12** (pinned in `pyproject.toml`).
- All deps installed from `pyproject.toml` (`pip install -e ".[sm1,sm2,figures,test]"`); never `pip install <pkg>` directly.
- SM2 is bit-for-bit reproducible on the same NumPy / scikit-learn versions (`np.random.default_rng(42)` for subsample draws; `KMeans(random_state=...)` everywhere).
- ARI = **0.9257** in this build; the paper reports 0.9445. The deviation is intentional: the paper's run used the legacy unseeded `np.random.choice` (non-reproducible across machines); we use a seeded `default_rng` so reviewers get identical numbers. Same K-Means partition, same typology counts (24 / 231 / 93 / 299 / 169) — see [`SM2/SM2_README.md`](SM2/SM2_README.md) for details.

## Data sources & licenses

- **Building footprints + heights** — Câmara Municipal da Amadora, 2009 large-scale topographic dataset (1:2000).
- **BGRI 2021 statistical blocks** — Instituto Nacional de Estatística (INE), Portuguese Census 2021.
- **DSM (LiDAR-derived, 0.5 m)** — Direção-Geral do Território (DGT), 2024.
- **Administrative boundaries of Amadora** — DGT, 2024.

All data are georeferenced to ETRS89 / PT-TM06 (EPSG:3763). Each dataset retains its original license; please consult the providers for terms of use.

## Citation

> Estanqueiro, R., Rebelo, C., & Tenedório, J. A. (2026). 3D Urban Structural Morphology at the Block Scale: A Geometric Vector Framework Based on Mean Building Volume, Height Variation Coefficient, and Mean Sky View Factor. *(submitted)*. (Manuscript DOI to be added on acceptance.)

This code archive is permanently archived on Zenodo: [https://doi.org/10.5281/zenodo.20113631](https://doi.org/10.5281/zenodo.20113631) (Concept DOI — always points to the latest version).

## Software author

**Rossana Estanqueiro** (sole author of the code in this repository).
Contact: rossana.estanqueiro@fcsh.unl.pt

When citing **the software**, use the Zenodo DOI of this repository (single author: R. Estanqueiro).

## Manuscript authors

The accompanying manuscript *(submitted)* is co-authored by:

**Rossana Estanqueiro¹,²,\*, Carla Rebelo², José António Tenedório¹,²**

¹ Universidade NOVA de Lisboa, Faculty of Social Sciences and Humanities, Department of Geography and Regional Planning, Avenida de Berna 26-C, 1069-061 Lisbon, Portugal
² Centre for Functional Ecology—Science for People & the Planet (CFE), University of Coimbra, History, Territories and Communities, Faculty of Social Sciences and Humanities (NOVA FCSH), Universidade NOVA de Lisboa, Associate Laboratory TERRA, Avenida de Berna 26-C, 1069-061 Lisbon, Portugal

\* Corresponding author: rossana.estanqueiro@fcsh.unl.pt

CRediT contribution roles for the manuscript: R. Estanqueiro — Conceptualization, Methodology, **Software**, Formal analysis, Validation, Investigation, Data curation, Writing—original draft, Visualization; C. Rebelo — Validation, Investigation, Writing—review and editing, Visualization; J. A. Tenedório — Conceptualization, Writing—review and editing.

## Acknowledgements

The authors thank **Francisco Pires** for his support with the Python implementation. The authors also acknowledge data provision by Câmara Municipal da Amadora (building footprints and building elevation points), Instituto Nacional de Estatística (BGRI 2021 statistical blocks), and the Directorate-General for Territory (DTM/DSM).

## Funding

This work is supported by FCT — Fundação para a Ciência e Tecnologia, I.P., in the framework of the Project UID/04004/2025 — Centre for Functional Ecology — Science for the People & the Planet, with DOI identifier [10.54499/UID/04004/2025](https://doi.org/10.54499/UID/04004/2025).

## License

[MIT](LICENSE).
