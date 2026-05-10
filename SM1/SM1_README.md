# SM1 — 3D Structural Metrics Computation

Computes three block-scale morphological metrics from building footprints + heights and a Sky View Factor raster:

| Metric | Description | Unit |
|---|---|---|
| **MBV** | Mean Building Volume per block | m³ |
| **HVC** | Height Variation Coefficient (CV of building heights per block) | dimensionless |
| **svf_mean** | Mean Sky View Factor per block (zonal stats) | 0–1 |

Case study: Amadora municipality, Portugal — 822 blocks total, 816 with complete metrics.

---

## Inputs

`SM1/input/` must contain:

- `buildings.shp` — building footprints with a per-building height field (denoted `H` in the article, Eq. 4: `H = Z_ridge − Z_ground`); CRS EPSG:3763. The script auto-detects the field via `resolve_height_column()` — recognised names are `H`, `altura` (Portuguese topographic data, e.g. Amadora), `Height`, or a `Z_ridge`/`Z_ground` (or `Cota_Cume`/`Cota_Solo`) pair. **Provided** (Amadora data uses `altura`).
- `blocks.shp` — BGRI 2021 blocks with `BGRI2021` (block ID) and `DTMNFR21` (parish code); CRS EPSG:3763. **Provided.**
- `svf.tif` — Sky View Factor raster. **NOT provided** (~1.9 GB) — generate it locally; see below.

See [`input/README.md`](input/README.md) for sources and licenses.

## Outputs

Written to `SM1/output/` (gitignored):

- `Block_Complete_Metrics.shp` — block geometries with all metrics (joinable in QGIS/ArcGIS).
- `BGRI_Complete_Metrics.csv` — tabular form. **Used as input by SM2.**

## Generating `svf.tif` (QGIS 3.34+ + SAGA GIS)

1. Load a 0.5 m DSM (e.g., DGT 2024 LiDAR-derived) in QGIS.
2. Processing Toolbox → SAGA → Terrain Analysis → Lighting → **Sky View Factor**.
3. Parameters:
   - Input DEM: `your_dsm.tif`
   - Max Search Radius: **100 m**
   - Number of Sectors: **32** (≈ 11.25° angular resolution)
   - Method: Cell size
4. Save the result to `SM1/input/svf.tif`.

## Running

From `final/` with the venv activated:

```powershell
.\.venv\Scripts\Activate.ps1     # if not already active
cd SM1
python SM1_Code_3D_Metrics.py
```

Dependencies are installed once via `pip install -e ".[sm1,sm2,figures,test]"` against the project's `pyproject.toml`. The `[sm1]` extra alone covers SM1: `pandas`, `numpy`, `geopandas`, `rasterstats`, `rasterio`.

## What the script does

1. Validates input file presence; exits with a hint if `svf.tif` is missing.
2. Loads buildings + blocks; reprojects buildings if CRS doesn't match.
3. Per-building volume `BV = footprint area × H` (Eq. 4 of the article).
4. Spatial join (centroid-in-polygon) → buildings → blocks.
5. Per block: `MBV = mean(volume)`, `HVC = std(height) / mean(height)` (`HVC = 0` if fewer than 2 buildings, or mean ≤ 0).
6. Per block: zonal-mean SVF.
7. Writes `Block_Complete_Metrics.shp` and `BGRI_Complete_Metrics.csv`.

## Skipping SM1 entirely

If you only want to reproduce SM2 + the figures, skip SVF generation and SM1 altogether — `SM2/input/BGRI_Complete_Metrics.csv` is the canonical SM1 output and is committed in this repo specifically so SM2 + figures are reproducible without an SVF raster.

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
