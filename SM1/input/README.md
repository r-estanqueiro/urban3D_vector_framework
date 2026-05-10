# SM1 inputs

This folder must contain three files for `SM1_Code_3D_Metrics.py` to run:

| File | What it is | Source / license | Provided here? |
|---|---|---|---|
| `buildings.shp` (+ `.shx`, `.dbf`, `.prj`, `.cpg`, `.shp.xml`) | Building footprints with a per-building height field (denoted `H` in the article, Eq. 4: `H = Z_ridge − Z_ground`); the Amadora source data names this field `altura`. CRS EPSG:3763 (PT-TM06), 17,747 features. The Python script auto-detects and renames the field to `H` on load. | Câmara Municipal da Amadora — 2009 large-scale topographic dataset (1:2000) | **YES** |
| `blocks.shp` (+ `.shx`, `.dbf`, `.prj`, `.cpg`, `.shp.xml`) | BGRI 2021 statistical subsections of Amadora; key columns `BGRI2021` (block ID) and `DTMNFR21` (parish code), CRS EPSG:3763, 822 features | INE — *Portuguese Census 2021 — Base Geográfica de Referenciação da Informação* | **YES** |
| `svf.tif` | Sky View Factor raster (continuous, 0–1) — radius 100 m, 32 sectors, derived from a 0.5 m DSM | DGT — LiDAR-derived DSM, 2024; SVF computed by the user with **QGIS + SAGA GIS** | **NO** — too large to distribute (~1.9 GB). Generate it locally; see top-level `SM1/SM1_README.md` |

## Why `svf.tif` isn't shipped

It's a 1.9 GB raster derived from open data. Generation takes a couple of minutes in QGIS+SAGA from the public DGT DSM. Step-by-step instructions are in [`../SM1_README.md`](../SM1_README.md). If you only want to reproduce the typology + figures (and not SM1), you can skip SVF generation entirely — see `SM2/input/BGRI_Complete_Metrics.csv` (the SM1→SM2 handoff is committed in this repo).

## Quick check

After placing `svf.tif` here, you should see:

```
SM1/input/
├── buildings.shp  buildings.shx  buildings.dbf  buildings.prj  buildings.cpg  buildings.shp.xml
├── blocks.shp     blocks.shx     blocks.dbf     blocks.prj     blocks.cpg     blocks.shp.xml
├── svf.tif
└── README.md
```
