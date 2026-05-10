"""
Supplementary Material SM1 — 3D Structural Metrics Computation

Computes three block-scale morphological metrics from building footprints,
their heights, and a Sky View Factor raster:

  - MBV       Mean Building Volume (m^3)         per block
  - HVC       Height Variation Coefficient       per block (std/mean of building heights H)
  - svf_mean  Mean Sky View Factor (0-1)         per block (zonal stats from SVF raster)

Notation follows the article (Eq. 4):
  H = Z_ridge - Z_ground          per-building height
  BV = footprint_area * H         per-building volume

Inputs (all in ./input/):
  - buildings.shp  Building footprints with a height field; CRS EPSG:3763.
                   The script accepts the height as `H` (paper notation), `altura`
                   (Portuguese topographic data, e.g. Amadora), or `Height`
                   (English alternative); or computes H on the fly from a
                   `Z_ridge`/`Z_ground` (or `Cota_Cume`/`Cota_Solo`) pair.
                   The detected field is internally renamed to `H`.
  - blocks.shp     BGRI 2021 statistical blocks with `BGRI2021` ID; CRS EPSG:3763
  - svf.tif        Sky View Factor raster generated externally with QGIS + SAGA
                   (see ./input/README.md and ../SM1_README.md for instructions)

Outputs (in ./output/):
  - Block_Complete_Metrics.shp   Joinable block shapefile with all metrics
  - BGRI_Complete_Metrics.csv    Tabular form, used as input by SM2

Run: python SM1_Code_3D_Metrics.py     (with SM1/.venv activated, from final/SM1/)
Software author: Rossana Estanqueiro <rossana.estanqueiro@fcsh.unl.pt>
Accompanying manuscript (submitted) co-authored with Carla Rebelo and José António Tenedório.
License: MIT
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from rasterstats import zonal_stats

warnings.filterwarnings("ignore")

SCRIPT_DIR = Path(__file__).parent
INPUT_DIR = SCRIPT_DIR / "input"
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

BUILDINGS_PATH = INPUT_DIR / "buildings.shp"
BLOCKS_PATH = INPUT_DIR / "blocks.shp"
SVF_RASTER_PATH = INPUT_DIR / "svf.tif"
OUTPUT_SHP = OUTPUT_DIR / "Block_Complete_Metrics.shp"
OUTPUT_CSV = OUTPUT_DIR / "BGRI_Complete_Metrics.csv"

BLOCK_ID_COL = "BGRI2021"
HEIGHT_COL = "H"  # paper notation (Eq. 4); the source field is renamed to this on load.


def resolve_height_column(buildings: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Map the source-data height field to `H` (paper notation, Eq. 4).

    Recognised inputs (in priority order):
      * `H` already present                      -> no-op (paper-native data)
      * `altura`                                  -> rename (Portuguese topographic data, e.g. Amadora)
      * `Height`                                  -> rename (English alternative)
      * `Z_ridge` and `Z_ground`                  -> compute H = Z_ridge - Z_ground (paper Eq. 4)
      * `Cota_Cume` and `Cota_Solo`               -> compute H = Cota_Cume - Cota_Solo (Portuguese cadastral data)
    """
    cols = set(buildings.columns)
    for source in ("H", "altura", "Height"):
        if source in cols:
            if source == HEIGHT_COL:
                return buildings
            return buildings.rename(columns={source: HEIGHT_COL})
    for ridge, ground in (("Z_ridge", "Z_ground"), ("Cota_Cume", "Cota_Solo")):
        if {ridge, ground} <= cols:
            buildings = buildings.copy()
            buildings[HEIGHT_COL] = buildings[ridge] - buildings[ground]
            return buildings
    raise ValueError(
        f"buildings.shp has no recognised height column. "
        f"Expected one of: 'H', 'altura', 'Height', or a 'Z_ridge'/'Z_ground' "
        f"(or 'Cota_Cume'/'Cota_Solo') pair to compute H = Z_ridge - Z_ground. "
        f"Available columns: {list(buildings.columns)}"
    )


def validate_inputs() -> None:
    missing = [p for p in (BUILDINGS_PATH, BLOCKS_PATH, SVF_RASTER_PATH) if not p.exists()]
    if not missing:
        return
    print("Missing input files:")
    for p in missing:
        print(f"  - {p}")
    if SVF_RASTER_PATH in missing:
        print(
            "\n  svf.tif must be generated externally (QGIS + SAGA, 100 m radius, 32 sectors)."
            "\n  See input/README.md and ../SM1_README.md for instructions."
        )
    sys.exit(1)


def compute_building_volumes(buildings: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if buildings.crs.is_geographic:
        raise ValueError("buildings must be in a projected CRS (e.g., EPSG:3763)")
    if "Shape_Area" in buildings.columns:
        area = buildings["Shape_Area"]
    else:
        area = buildings.geometry.area
    buildings = buildings.copy()
    buildings["volume_m3"] = area * buildings[HEIGHT_COL]
    return buildings


def compute_block_metrics(
    blocks: gpd.GeoDataFrame, buildings: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """MBV and HVC per block via centroid-in-polygon spatial join."""
    centroids = buildings.copy()
    centroids["geometry"] = buildings.geometry.centroid
    joined = gpd.sjoin(
        centroids,
        blocks[[BLOCK_ID_COL, "geometry"]],
        how="inner",
        predicate="within",
    )
    grouped = joined.groupby(BLOCK_ID_COL)
    mbv = grouped["volume_m3"].mean().rename("MBV")

    def cv(heights: pd.Series) -> float:
        if len(heights) < 2:
            return 0.0
        m = heights.mean()
        return heights.std() / m if m > 0 else 0.0

    hvc = grouped[HEIGHT_COL].apply(cv).rename("HVC")
    metrics = pd.concat([mbv, hvc], axis=1)
    return blocks.merge(metrics, on=BLOCK_ID_COL, how="left")


def compute_mean_svf(blocks: gpd.GeoDataFrame, svf_path: Path) -> gpd.GeoDataFrame:
    stats = zonal_stats(blocks, str(svf_path), stats="mean", geojson_out=False)
    blocks = blocks.copy()
    blocks["svf_mean"] = [
        s["mean"] if s and s.get("mean") is not None else np.nan for s in stats
    ]
    return blocks


def main() -> None:
    print("SM1 — 3D Urban Structural Metrics")
    print("=" * 60)
    validate_inputs()

    print(f"Loading {BUILDINGS_PATH.name} ...")
    buildings = gpd.read_file(BUILDINGS_PATH)
    print(f"  {len(buildings)} buildings, CRS={buildings.crs}")

    print(f"Loading {BLOCKS_PATH.name} ...")
    blocks = gpd.read_file(BLOCKS_PATH)
    print(f"  {len(blocks)} blocks, CRS={blocks.crs}")

    if buildings.crs != blocks.crs:
        print(f"  reprojecting buildings {buildings.crs} -> {blocks.crs}")
        buildings = buildings.to_crs(blocks.crs)

    buildings = resolve_height_column(buildings)
    if BLOCK_ID_COL not in blocks.columns:
        raise ValueError(
            f"blocks.shp is missing the '{BLOCK_ID_COL}' column. "
            f"Available: {list(blocks.columns)}"
        )

    print(f"Computing per-building volume BV = footprint_area * {HEIGHT_COL} ...")
    buildings = compute_building_volumes(buildings)
    print(f"  mean volume: {buildings['volume_m3'].mean():,.0f} m^3")

    print("Aggregating block-level metrics (MBV, HVC) ...")
    blocks = compute_block_metrics(blocks, buildings)

    print("Computing zonal mean SVF ...")
    blocks = compute_mean_svf(blocks, SVF_RASTER_PATH)

    blocks.to_file(OUTPUT_SHP)
    blocks.drop(columns="geometry").to_csv(OUTPUT_CSV, index=False)

    valid = blocks.dropna(subset=["MBV", "HVC", "svf_mean"])
    print()
    print(f"Wrote {OUTPUT_SHP.name} and {OUTPUT_CSV.name} to {OUTPUT_DIR}")
    print(f"Valid blocks (no NaN in metrics): {len(valid)} / {len(blocks)}")
    print(valid[["MBV", "HVC", "svf_mean"]].describe().round(3))


if __name__ == "__main__":
    main()
