# Analysis Scripts — Execution Guide

**Study:** What Explains Regional Benzodiazepine Prescribing Variation Under Universal Health Coverage? A Nationwide Ecological Study from Japan  
**Authors:** Saito H, Ohira T  
**Data:** NDB Open Data No.10 (FY 2023) + 2020 National Census

---

## Execution Order

Run all scripts from the **project root directory** in numerical order.

```bash
# From project root:
python 03_Analysis/scripts/01_extract_bz_drugs.py
python 03_Analysis/scripts/02_fetch_census_isolation.py
python 03_Analysis/scripts/03_load_secondary_outcomes.py
python 03_Analysis/scripts/04_integrate_dataset.py
python 03_Analysis/scripts/05_ols_regression.py
python 03_Analysis/scripts/06_spatial_autocorrelation.py
python 03_Analysis/scripts/07_visualization.py
```

---

## Script Descriptions

| Script | Input | Output | Description |
|--------|-------|--------|-------------|
| `01_extract_bz_drugs.py` | `data/raw/NDB/` | `data/interim/bz_drug_rate.csv` | Extract BZ receptor agonist prescription volume (drug codes 112, 117) from NDB Open Data No.10; compute per-100,000 population rate by prefecture |
| `02_fetch_census_isolation.py` | `data/raw/census/` | `data/interim/solo_elderly_rate.csv` | Compute solo elderly rate (single-person households aged ≥65 / total population aged ≥65) from 2020 National Census mesh CSV files (47 prefectures) |
| `03_load_secondary_outcomes.py` | `data/raw/NDB/` | `data/interim/secondary_outcomes.csv` | Extract secondary outcomes: home care utilization rate and psychiatric specialist therapy rate from NDB Open Data No.10 |
| `04_integrate_dataset.py` | `data/interim/*.csv` | `03_Analysis/results/analysis_dataset.csv` | Merge all intermediate datasets into the final analysis dataset (N = 47 prefectures); add aging rate, population density, per-capita income |
| `05_ols_regression.py` | `03_Analysis/results/analysis_dataset.csv` | `03_Analysis/results/regression_main.csv`, `sensitivity_analysis.csv`, `secondary_outcomes.csv` | OLS regression with HC3 robust standard errors (main model); 6 sensitivity specifications; secondary outcomes |
| `06_spatial_autocorrelation.py` | `03_Analysis/results/analysis_dataset.csv` | `03_Analysis/results/moran_results.csv`, `lisa_results.csv` | Global Moran's I (Queen contiguity, row-standardized, 999 permutations); LISA cluster analysis; KNN=2 supplementation for island prefectures |
| `07_visualization.py` | `03_Analysis/results/*.csv` | `03_Analysis/results/fig1_choropleth_bz_rate.png` … `lisa_cluster_map.png` | Generate all manuscript figures (choropleth map, forest plot, scatter plots, Moran scatter, LISA cluster map) |

---

## Data Flow

```
data/raw/NDB/           → 01 → data/interim/bz_drug_rate.csv
data/raw/census/        → 02 → data/interim/solo_elderly_rate.csv
data/raw/NDB/           → 03 → data/interim/secondary_outcomes.csv
data/interim/*.csv      → 04 → 03_Analysis/results/analysis_dataset.csv
analysis_dataset.csv    → 05 → regression_main.csv + sensitivity_analysis.csv
analysis_dataset.csv    → 06 → moran_results.csv + lisa_results.csv
results/*.csv           → 07 → fig1–fig4 + lisa_cluster_map (PNG)
```

---

## Skipping the Raw Data Pipeline

The final analysis dataset is included in `data/release/social_isolation_bz_analysis_dataset.csv`.  
Copy it to `03_Analysis/results/analysis_dataset.csv` and run scripts 05–07 directly:

```bash
cp data/release/social_isolation_bz_analysis_dataset.csv 03_Analysis/results/analysis_dataset.csv
python 03_Analysis/scripts/05_ols_regression.py
python 03_Analysis/scripts/06_spatial_autocorrelation.py
python 03_Analysis/scripts/07_visualization.py
```

---

## Environment

- Python 3.14
- See [`requirements.txt`](../../requirements.txt) for package versions
- Configuration (drug codes, file paths): [`config/config.yaml`](../../config/config.yaml)
