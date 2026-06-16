# Social Isolation and Benzodiazepine Prescribing Disparities in Japan

**A Prefecture-Level Ecological Study**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **GitHub repository:** https://github.com/haruki00430/NDB_XXX_social_isolation_bz

## Overview

This repository contains the analysis code, aggregate data (N = 47 prefectures), and manuscript source for a cross-sectional ecological study examining whether the prefecture-level prevalence of older adults living alone explains regional variation in benzodiazepine (BZ) receptor agonist prescribing in Japan.

**Key findings:**

- The solo elderly rate (proportion of older adults aged ≥65 years living alone) was **not** significantly associated with BZ prescription volume (β = 838,000 per 100,000; p = 0.856; **0/6** sensitivity specifications)
- Aging rate was the only robust predictor (β = 151,480; p = 0.008; **6/6** specifications; R² = 0.322)
- BZ prescribing showed significant positive spatial autocorrelation (Moran's I = 0.348; p = 0.003)

## Data Sources

| Source | Content | Year |
|--------|---------|------|
| NDB Open Data (10th edition) | BZ prescription volume (drug codes 112, 117) by prefecture | FY2023 |
| 2020 National Census | Single-person households aged ≥65 years (solo elderly rate) | 2020 |
| Population Estimates | Prefecture-level total population and aging rate | 2023 |
| Cabinet Office | Per capita prefectural income | FY2021 |

See [DATA_SOURCES.md](DATA_SOURCES.md) for full details and URLs.

## Repository Structure

```
NDB_XXX_social_isolation_bz/
├── 03_Analysis/
│   ├── scripts/                    # Analysis scripts (run in order 01→07)
│   │   ├── 01_extract_bz_drugs.py
│   │   ├── 02_fetch_census_isolation.py
│   │   ├── 03_load_secondary_outcomes.py
│   │   ├── 04_integrate_dataset.py
│   │   ├── 05_ols_regression.py
│   │   ├── 06_spatial_autocorrelation.py
│   │   └── 07_visualization.py
│   └── results/                    # Output figures (PNG)
├── 04_Manuscripts/
│   ├── 09Manuscript_social_isolation_bz_AGG_submission.qmd   # Submission manuscript (QMD)
│   ├── highlights_social_isolation_bz.qmd
│   ├── references.bib
│   └── apa.csl
├── config/
│   └── config.yaml                 # Drug codes, thresholds
├── data/
│   └── release/                    # Aggregate data for reproducibility (N=47, no individual data)
├── CITATION.cff
├── REPRODUCE.md
├── DATA_SOURCES.md
└── LICENSE
```

## Reproducing the Analysis

See [REPRODUCE.md](REPRODUCE.md) for step-by-step instructions.

**Quick start:**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place NDB Open Data (10th edition) in data/raw/NDB/ (not included; publicly available)

# 3. Run scripts in order
python 03_Analysis/scripts/01_extract_bz_drugs.py
python 03_Analysis/scripts/02_fetch_census_isolation.py
python 03_Analysis/scripts/03_load_secondary_outcomes.py
python 03_Analysis/scripts/04_integrate_dataset.py
python 03_Analysis/scripts/05_ols_regression.py
python 03_Analysis/scripts/06_spatial_autocorrelation.py
python 03_Analysis/scripts/07_visualization.py
```

The aggregate analysis dataset (N=47 prefectures) is included in `data/release/` for direct use without running the full pipeline.

## Citation

If you use this code or data, please cite:

> Saito, H. (2026). *Social Isolation and Benzodiazepine Prescribing Disparities in Japan: A Prefecture-Level Ecological Study* [Data and code]. Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX

See [CITATION.cff](CITATION.cff) for machine-readable citation metadata.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Author

**Haruki Saito**  
Fukushima Medical University School of Medicine, Fukushima, Japan  
m211039@fmu.ac.jp

## Ethics Statement

This study used publicly available, de-identified, aggregate-level administrative data (NDB Open Data and National Census). No individual-level data were accessed. No ethics committee approval was required under applicable Japanese national guidelines for secondary research using publicly available aggregate statistics.
