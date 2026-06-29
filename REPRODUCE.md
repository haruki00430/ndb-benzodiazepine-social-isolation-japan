# Reproducibility Guide

This document describes how to reproduce the analysis in:

> Saito H, Ohira T. What Explains Regional Benzodiazepine Prescribing Variation Under Universal Health Coverage? A Nationwide Ecological Study from Japan. *Social Psychiatry and Psychiatric Epidemiology*. [Submitted 2026].

---

## Prerequisites

### Software

- Python 3.14 or later
- Quarto 1.4 or later (for manuscript rendering only)

### Python packages

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pandas numpy matplotlib seaborn geopandas statsmodels scipy libpysal esda pyyaml openpyxl requests
```

### Versions used in original analysis

| Package | Version |
|---------|---------|
| pandas | 2.x |
| numpy | 2.x |
| statsmodels | 0.14 |
| libpysal | 4.9 |
| esda | 2.5 |
| geopandas | 0.14 |

---

## Data Requirements

### Included in this repository (`data/release/`)

The aggregate analysis dataset (N = 47 prefectures, no individual-level data) is included and can be used directly:

| File | Contents |
|------|---------|
| `social_isolation_bz_analysis_dataset.csv` | Main analysis dataset (all variables, N=47) |
| `social_isolation_bz_descriptive_stats.csv` | Table 1 descriptive statistics |
| `social_isolation_bz_regression_main.csv` | Main OLS regression results |
| `social_isolation_bz_sensitivity_analysis.csv` | Sensitivity analyses (6 specifications) |
| `social_isolation_bz_secondary_outcomes.csv` | Secondary outcomes regression |
| `social_isolation_bz_moran_results.csv` | Global Moran's I results |
| `social_isolation_bz_lisa_results.csv` | LISA cluster results |

### NDB Open Data (not included — must download separately)

Source: Ministry of Health, Labour and Welfare of Japan  
URL: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html  
Required: NDB Open Data No.10 — Drug effect classification section (薬効分類 112, 117)

Place downloaded files in: `data/raw/NDB/`

### National Census data (not included — must download separately)

Source: Statistics Bureau, Ministry of Internal Affairs and Communications  
URL: https://www.e-stat.go.jp/  
Required: 2020 National Census — Single-person households aged ≥65 years by prefecture (mesh-level CSV files)

Place downloaded files in: `data/raw/census/`

### Shapefile for mapping (not included — must download separately)

Source: National Land Numerical Information, Ministry of Land, Infrastructure, Transport and Tourism  
URL: https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2024.html  
Required: Administrative boundary shapefile (prefecture level)

Place in: `data/raw/MLIT_N03/`

---

## Running the Analysis

Execute the scripts in numerical order from the project root.  
See [`03_Analysis/scripts/README.md`](03_Analysis/scripts/README.md) for full details.

```bash
# Step 1: Extract BZ drug prescription data from NDB Open Data
python 03_Analysis/scripts/01_extract_bz_drugs.py

# Step 2: Extract solo elderly rate from National Census
python 03_Analysis/scripts/02_fetch_census_isolation.py

# Step 3: Load secondary outcome variables
python 03_Analysis/scripts/03_load_secondary_outcomes.py

# Step 4: Integrate all data into analysis dataset (N=47)
python 03_Analysis/scripts/04_integrate_dataset.py

# Step 5: Run OLS regression (HC3 robust SE + 6 sensitivity specifications)
python 03_Analysis/scripts/05_ols_regression.py

# Step 6: Run spatial autocorrelation (Moran's I, LISA)
python 03_Analysis/scripts/06_spatial_autocorrelation.py

# Step 7: Generate all figures (Figure 1–4 + LISA cluster map)
python 03_Analysis/scripts/07_visualization.py
```

**Expected outputs:**

| Script | Output location |
|--------|----------------|
| 04 | `03_Analysis/results/analysis_dataset.csv` |
| 05 | `03_Analysis/results/regression_main.csv`, `sensitivity_analysis.csv` |
| 06 | `03_Analysis/results/moran_results.csv`, `lisa_results.csv` |
| 07 | `03_Analysis/results/fig1_choropleth_bz_rate.png` through `lisa_cluster_map.png` |

---

## Skipping the Full Pipeline

If you only want to reproduce the statistical results using the pre-built aggregate dataset:

```python
import pandas as pd

df = pd.read_csv("data/release/social_isolation_bz_analysis_dataset.csv")
print(df.shape)   # Should be (47, ~15)
```

Then run scripts 05–07 directly (they read from `03_Analysis/results/analysis_dataset.csv`; copy the release CSV there first).

---

## Notes on Reproducibility

- All random seeds are fixed (where applicable)
- The analysis is deterministic given the same input data
- Spatial weights use Queen contiguity + K=2 KNN supplementation for island prefectures (Okinawa)
- HC3 robust standard errors are computed via `statsmodels.stats.sandwich_covariance`
- 999 permutations used for Moran's I significance testing
