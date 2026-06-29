# Social Isolation and Benzodiazepine Prescribing Disparities in Japan

**A Prefecture-Level Ecological Study (N = 47 Prefectures, FY 2023 NDB Open Data)**

> **Reproduce · Public-data only:** [`REPRODUCE.md`](REPRODUCE.md) · [`DATA_SOURCES.md`](DATA_SOURCES.md) · [`03_Analysis/scripts/README.md`](03_Analysis/scripts/README.md) · [`CITATION.cff`](CITATION.cff)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20713830.svg)](https://doi.org/10.5281/zenodo.20713830)

> **日本語概要は下部の「概要（日本語）」セクションを参照してください。**

---

## Overview

This repository contains the analysis code, aggregate prefecture-level data (N = 47), and manuscript source for the study:

> Saito H, Ohira T. What Explains Regional Benzodiazepine Prescribing Variation Under Universal Health Coverage? A Nationwide Ecological Study from Japan. *Social Psychiatry and Psychiatric Epidemiology*. [Submitted 2026].

We examined whether the **prefecture-level prevalence of older adults living alone** (solo elderly rate, 2020 National Census) explains regional variation in **benzodiazepine (BZ) receptor agonist prescribing** across all 47 Japanese prefectures, using NDB Open Data No.10 (FY 2023) and spatial ecological methods.

---

## Key Findings

- The solo elderly rate was **not** significantly associated with BZ prescription volume (β = 838,000 per 100,000; *p* = 0.856; **0/6** sensitivity specifications)
- **Aging rate** was the only robust predictor (β = 151,480; *p* = 0.008; **6/6** specifications; R² = 0.322)
- BZ prescribing showed significant positive spatial autocorrelation (Global Moran's I = 0.348; *p* = 0.003)
- Under Japan's universal health coverage, geographic prescribing variation appears driven by demographic composition and unmeasured supply-side factors rather than social isolation as measured by living-alone prevalence

---

## Data Sources

| Variable | Source | Year |
|---------|--------|------|
| BZ prescription volume (drug codes 112, 117) | NDB Open Data No.10 (FY 2023) | Ministry of Health, Labour and Welfare |
| Solo elderly rate (single-person households aged ≥65 years) | 2020 National Census | Statistics Bureau of Japan |
| Total population, aging rate | Population estimates | Statistics Bureau of Japan |
| Per-capita prefectural income | Prefectural accounts | Cabinet Office of Japan |
| Prefecture boundaries (shapefile) | National Land Numerical Information (N03) | MLIT |

See [DATA_SOURCES.md](DATA_SOURCES.md) for full details and download URLs.

**Note:** NDB raw data are not included in this repository. They are publicly available at:  
https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html

---

## Repository Structure

```
ndb-benzodiazepine-social-isolation-japan/
├── README.md
├── LICENSE                              # MIT License
├── requirements.txt                     # Python dependencies
├── config/
│   └── config.yaml                      # Drug codes, thresholds, file paths
├── 03_Analysis/
│   ├── scripts/                         # Analysis scripts (run in order 01→07)
│   │   ├── README.md                    # Execution guide
│   │   ├── 01_extract_bz_drugs.py       # Extract BZ prescription data from NDB
│   │   ├── 02_fetch_census_isolation.py # Extract solo elderly rate from Census
│   │   ├── 03_load_secondary_outcomes.py
│   │   ├── 04_integrate_dataset.py      # Build analysis dataset (N=47)
│   │   ├── 05_ols_regression.py         # OLS + HC3 robust SE + 6 sensitivity specs
│   │   ├── 06_spatial_autocorrelation.py # Global Moran's I + LISA
│   │   └── 07_visualization.py          # Figures 1–4 + LISA cluster map
│   └── results/                         # Output figures (PNG)
├── data/
│   └── release/                         # Aggregate data (N=47, no individual data)
│       ├── social_isolation_bz_analysis_dataset.csv
│       ├── social_isolation_bz_regression_main.csv
│       ├── social_isolation_bz_sensitivity_analysis.csv
│       ├── social_isolation_bz_secondary_outcomes.csv
│       ├── social_isolation_bz_moran_results.csv
│       ├── social_isolation_bz_lisa_results.csv
│       └── social_isolation_bz_descriptive_stats.csv
├── 04_Manuscripts/
│   ├── Manuscript_social_isolation_bz.qmd   # Quarto source
│   ├── references.bib                        # BibTeX references
│   └── vancouver.csl                         # Vancouver citation style
├── CITATION.cff
├── REPRODUCE.md
└── DATA_SOURCES.md
```

---

## Requirements

Python 3.14 is used in the development environment.

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

Key packages: `pandas`, `numpy`, `geopandas`, `statsmodels`, `libpysal`, `esda`, `matplotlib`, `seaborn`, `scipy`, `openpyxl`

---

## Usage

See [REPRODUCE.md](REPRODUCE.md) for full step-by-step instructions.  
See [03_Analysis/scripts/README.md](03_Analysis/scripts/README.md) for script execution order.

```bash
# Run scripts in numbered order from project root
python 03_Analysis/scripts/01_extract_bz_drugs.py
python 03_Analysis/scripts/02_fetch_census_isolation.py
python 03_Analysis/scripts/03_load_secondary_outcomes.py
python 03_Analysis/scripts/04_integrate_dataset.py
python 03_Analysis/scripts/05_ols_regression.py
python 03_Analysis/scripts/06_spatial_autocorrelation.py
python 03_Analysis/scripts/07_visualization.py
```

The aggregate analysis dataset (N = 47 prefectures) is included in `data/release/` and can be used directly to reproduce statistical results without running the full pipeline.

---

## License

Code and data in this repository are released under the [MIT License](LICENSE).

NDB raw Excel files are not redistributed; they are subject to the terms of use set by the Ministry of Health, Labour and Welfare of Japan.

---

## Citation

If you use this code or data, please cite:

```
Saito H, Ohira T. What Explains Regional Benzodiazepine Prescribing Variation
Under Universal Health Coverage? A Nationwide Ecological Study from Japan.
Social Psychiatry and Psychiatric Epidemiology. [Submitted 2026].
```

Or use the Zenodo DOI (see [`CITATION.cff`](CITATION.cff)):  
`https://doi.org/10.5281/zenodo.20713830`

---

## Authors / 著者

**Haruki Saito** (Corresponding author)  
Department of Epidemiology, Fukushima Medical University School of Medicine  
1 Hikarigaoka, Fukushima-shi, Fukushima 960-1295, Japan  
Email: m211039@fmu.ac.jp · ORCID: [0009-0009-7890-6068](https://orcid.org/0009-0009-7890-6068)

**Tetsuya Ohira**  
Department of Epidemiology, Fukushima Medical University School of Medicine, Fukushima, Japan  
Radiation Medical Science Center for the Fukushima Health Management Survey, Fukushima Medical University, Fukushima, Japan  
ORCID: [0000-0003-4532-7165](https://orcid.org/0000-0003-4532-7165)

---

## Ethics Statement

This study used publicly available, de-identified, aggregate-level administrative data (NDB Open Data and National Census). No individual-level data were accessed. No ethics committee approval was required under applicable Japanese national guidelines for secondary research using publicly available aggregate statistics.

---

---

## 概要（日本語）

### 研究タイトル

「ユニバーサルヘルスカバレッジ下でのベンゾジアゼピン系薬剤処方の地域格差を規定する要因：日本全国生態学的研究」

### 背景・目的

日本は世界最速で高齢化が進む社会であり、高齢者の独居率も高い。社会的孤立（独居率をプロキシとして使用）がBZ系薬剤（抗不安薬・睡眠薬）の都道府県別処方格差を説明するかを、NDBオープンデータ第10回（FY2023）と2020年国勢調査データを用いて横断的生態学的研究で検証しました。

### 主要結果

- **独居老人率**（65歳以上単独世帯割合）は BZ 処方量と有意な関連なし（β = 838,000、*p* = 0.856、感度分析 **0/6** 仕様で有意）
- **高齢化率**が唯一の頑健な予測因子（β = 151,480、*p* = 0.008、**6/6** 仕様で有意、R² = 0.322）
- BZ 処方量に有意な正の空間的自己相関あり（Global Moran's I = 0.348、*p* = 0.003）
- ユニバーサルヘルスカバレッジ下では、処方格差は患者の社会的孤立より医療供給側・地域処方文化といった要因で規定される可能性が示唆された

### 解釈

本研究は「需要側（社会的孤立）ではなく供給側・地域特性が処方格差を規定する」という日本の生態学的研究で一貫したパターンの追加的証拠を提供します。不適切なBZ使用を減らすためには、医師への処方教育、地域ガイドライン実装、減薬支援システムの整備が重要と考えられます。

### データ・コード

- NDB生データ：[厚生労働省NDBオープンデータ](https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html)（要手動ダウンロード）
- 解析コード・都道府県別集計値（N=47、個票なし）：本リポジトリ（MIT License）
- Zenodo アーカイブ：https://doi.org/10.5281/zenodo.20713830

### 実行環境

```bash
pip install -r requirements.txt
python 03_Analysis/scripts/01_extract_bz_drugs.py
# ... (03_Analysis/scripts/README.md の実行順序を参照)
```

### 投稿先

*Social Psychiatry and Psychiatric Epidemiology* (Springer Nature, 投稿済み 2026)

### ライセンス

解析コード・集計データ：[MIT License](LICENSE)

---

*Last updated: 2026-06-29*
