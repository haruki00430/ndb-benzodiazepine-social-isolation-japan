# Data Sources

This document describes all data sources used in the analysis.

## 1. NDB Open Data (10th Edition) — Primary Outcome

**Provider:** Ministry of Health, Labour and Welfare of Japan (厚生労働省)  
**URL:** https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html  
**Fiscal year:** FY2023 (令和5年度) receipts  
**Access:** Publicly available (no registration required)  
**Format:** Excel (.xlsx), MultiIndex headers (rows 3–4)

**Variables extracted:**

| Variable | NDB table | Drug codes |
|----------|-----------|------------|
| BZ prescription volume (primary outcome) | 処方薬・薬効分類別数量 | 112 (催眠鎮静剤), 117 (精神神経用剤) |
| Home care patient volume (secondary) | 在宅医療 | — |
| Psychiatric specialty therapy volume (secondary) | 精神科専門療法 | — |

**Note:** Drug codes 112 and 117 encompass benzodiazepines, Z-drugs (non-benzodiazepine hypnotics), and related agents. Individual substance-level disaggregation is not available in the open-access edition.

## 2. 2020 National Census — Primary Exposure

**Provider:** Statistics Bureau, Ministry of Internal Affairs and Communications (総務省統計局)  
**URL:** https://www.e-stat.go.jp/  
**Survey year:** October 1, 2020 (令和2年国勢調査)  
**Access:** Publicly available via e-Stat portal  
**Format:** CSV / Excel

**Variables extracted:**

| Variable | Description |
|----------|-------------|
| Solo elderly rate (exposure) | Single-person general households with householder aged ≥65 years ÷ total population aged ≥65 years, by prefecture |

**Definition:** Solo elderly rate = (65歳以上単独世帯数) / (65歳以上人口)

## 3. Population Estimates 2023 — Covariates

**Provider:** Statistics Bureau, Ministry of Internal Affairs and Communications  
**URL:** https://www.stat.go.jp/data/jinsui/  
**Reference date:** October 1, 2023  
**Access:** Publicly available

**Variables extracted:**

| Variable | Description |
|----------|-------------|
| Aging rate | Population aged ≥65 years ÷ total population, by prefecture |
| Population density | Persons per km², by prefecture |

## 4. Prefectural Income — Covariate

**Provider:** Cabinet Office (内閣府)  
**URL:** https://www.esri.cao.go.jp/jp/sna/data/data_list/kenmin/files/files_kenmin.html  
**Fiscal year:** FY2021 (令和3年度)  
**Access:** Publicly available

**Variable:** Per capita prefectural income (千円/人), by prefecture

## 5. Administrative Boundary Shapefile — Visualization only

**Provider:** National Land Numerical Information, Ministry of Land, Infrastructure, Transport and Tourism  
**URL:** https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2024.html  
**Format:** Shapefile (.shp)  
**Access:** Publicly available (free download)

Used only for choropleth map generation (Figure 1, Figure 5). Not included in this repository due to file size.

## Data Not Included in This Repository

The following raw data files are **not included** in this repository in compliance with NDB data usage guidelines and to keep repository size manageable:

- NDB Open Data Excel files (`data/raw/NDB/`)
- National Census CSV files (`data/raw/census/`)
- Administrative boundary shapefiles (`data/raw/MLIT_N03/`)

All raw data are publicly available at the URLs listed above. The aggregate analysis dataset (N=47 prefectures) derived from these sources is included in `data/release/` for reproducibility.

## Aggregate Data Included (`data/release/`)

The following aggregate files are included and contain **no individual-level data**:

| File | Description | N |
|------|-------------|---|
| `social_isolation_bz_analysis_dataset.csv` | Main analysis dataset (all variables) | 47 |
| `social_isolation_bz_descriptive_stats.csv` | Descriptive statistics (Table 1) | 47 |
| `social_isolation_bz_regression_main.csv` | Main OLS regression results (Table 2) | — |
| `social_isolation_bz_sensitivity_analysis.csv` | Six sensitivity analyses (Suppl. Table S1) | — |
| `social_isolation_bz_secondary_outcomes.csv` | Secondary outcome regression (Table 3) | — |
| `social_isolation_bz_moran_results.csv` | Global Moran's I results | — |
| `social_isolation_bz_lisa_results.csv` | LISA cluster classification (N=47) | 47 |
