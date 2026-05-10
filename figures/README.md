# Figures

Per-figure scripts that **load** SM2's persisted artifacts and write a single image each, in **JPEG** format at **600 DPI** (quality 95). They never re-run K-Means or consensus — random-seeded steps live in SM2 and are persisted; the figures consume those artifacts so they always match the typology assignment in `SM2/output/BGRI_Final_Typology_k5_Production.csv`.

## Prerequisite

Run SM2 first:

```powershell
.\.venv\Scripts\Activate.ps1
cd SM2
python SM2_Code_Typology_Consensus.py
cd ..
```

That populates `SM2/output/` with `BGRI_Final_Typology_k5_Production.csv`, `consensus_matrix_k5.npy`, and `inertia_k2_to_9.npy` — everything the figure scripts need.

## Article figures (in scope)

| Script | Output | Inputs read |
|---|---|---|
| [`article/fig03_elbow.py`](article/fig03_elbow.py) | `Figure_03_Elbow_Method_Optimal_K.jpg` | `inertia_k2_to_9.npy` |
| [`article/fig04_consensus_matrix.py`](article/fig04_consensus_matrix.py) | `Figure_04_Consensus_Matrix_k5.jpg` | `consensus_matrix_k5.npy` + typology CSV (for ordering) |
| [`article/fig05_kmeans_vs_consensus.py`](article/fig05_kmeans_vs_consensus.py) | `Figure_05_Kmeans_vs_Consensus_Agreement.jpg` | typology CSV (`cluster_ordered`, `consensus_ordered`) |
| [`article/fig06_radar_profiles.py`](article/fig06_radar_profiles.py) | `Figure_06_Radar_Profiles_Five_Typologies.jpg` | typology CSV (`MBV_z`, `HVC_z`, `svf_mean_z`, `cluster_ordered`) |
| [`article/fig07_boxplots.py`](article/fig07_boxplots.py) | `Figure_07_Boxplots_Structural_Metrics.jpg` | typology CSV (`MBV`, `HVC`, `svf_mean`, `cluster_ordered`) |
| [`article/fig08_pairwise_scatter.py`](article/fig08_pairwise_scatter.py) | `Figure_08_Pairwise_Scatter_Standardized.jpg` | typology CSV (`MBV_z`, `HVC_z`, `svf_mean_z`, `cluster_ordered`) |
| [`article/fig10_typologies_by_parish.py`](article/fig10_typologies_by_parish.py) | `Figure_10_Typologies_by_Parish.jpg` | typology CSV (`cluster_ordered`, `DTMNFR21`) |

## Supplementary Material SM2 figures (parish analysis, in scope)

| Script | Output | Inputs read |
|---|---|---|
| [`supplementary_sm2/figSM2_01_heatmap_freq_parish.py`](supplementary_sm2/figSM2_01_heatmap_freq_parish.py) | `Figure_SM2_01_Heatmap_Typology_Frequency_Parish.jpg` | typology CSV |
| [`supplementary_sm2/figSM2_02_heatmap_counts_parish.py`](supplementary_sm2/figSM2_02_heatmap_counts_parish.py) | `Figure_SM2_02_Heatmap_Block_Count_Parish.jpg` | typology CSV |
| [`supplementary_sm2/figSM2_03_normalized_profile_parish.py`](supplementary_sm2/figSM2_03_normalized_profile_parish.py) | `Figure_SM2_03_Normalized_Profile_Parish.jpg` | typology CSV |
| [`supplementary_sm2/figSM2_04_pie_charts_parish.py`](supplementary_sm2/figSM2_04_pie_charts_parish.py) | `Figure_SM2_04_Pie_Charts_Composition_Parish.jpg` | typology CSV |

## Out of scope

Figures 01, 02, 09 of the main article (study-area map, methodology flowchart, spatial distribution map) are not produced by Python scripts — they are GIS / vector compositions and are not regenerated here.

## Running

Individually:

```powershell
python figures/article/fig06_radar_profiles.py
```

Or all at once from `final/`:

```powershell
Get-ChildItem figures\article\*.py, figures\supplementary_sm2\*.py |
  ForEach-Object { python $_.FullName }
```

Outputs land in `figures/output/{article,supplementary_sm2}/` (gitignored).
