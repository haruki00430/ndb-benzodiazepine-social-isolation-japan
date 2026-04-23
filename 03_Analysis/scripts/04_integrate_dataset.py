# -*- coding: utf-8 -*-
"""
04_integrate_dataset.py
BZ処方・独居老人率・副アウトカム・共変量を結合して解析用データセットを作成する。

転用元: projects/NDB_XXX_poverty_tgi/03_Analysis/scripts/03_integrate_dataset.py

入力:
  03_Analysis/results/bz_prefecture.csv
  03_Analysis/results/census_isolation.csv
  03_Analysis/results/secondary_outcomes.csv
  ../NDB_XXX_poverty_tgi/03_Analysis/results/covariates.csv

出力:
  03_Analysis/results/analysis_dataset.csv
    主要変数:
      bz_drug_rate        : BZ処方量/人口10万人（外来: 院外+院内）
      bz_drug_rate_all    : BZ処方量/人口10万人（外来+入院）
      solo_elderly_rate   : 独居老人率（2020年国勢調査）
      homecare_rate       : 在宅医療患者数/65歳以上人口10,000人
      psychiatry_rate     : 精神科専門療法料患者数/人口10万人
      aging_rate          : 高齢化率（%）
      pop_density         : 人口密度（人/km²）
      income_per_capita   : 1人当たり県民所得（千円）
      pa_rate_permil      : 生活保護率（人口千人当たり）
"""

from pathlib import Path
import pandas as pd
import numpy as np

# パス設定
SCRIPT_DIR  = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parents[1]
PROJECT_ROOT = SCRIPT_DIR.parents[3]

RESULTS_DIR = SCRIPT_DIR.parent / "results"
BZ_FILE     = RESULTS_DIR / "bz_prefecture.csv"
ISO_FILE    = RESULTS_DIR / "census_isolation.csv"
SEC_FILE    = RESULTS_DIR / "secondary_outcomes.csv"
COV_FILE    = (PROJECT_ROOT / "projects" / "NDB_XXX_poverty_tgi"
               / "03_Analysis" / "results" / "covariates.csv")
OUT_FILE    = RESULTS_DIR / "analysis_dataset.csv"


def main():
    print("=" * 60)
    print(" 04_integrate_dataset.py  データ統合")
    print("=" * 60)

    # ----------------------------------------------------------
    # 1. 読み込み
    # ----------------------------------------------------------
    bz  = pd.read_csv(BZ_FILE,  encoding="utf-8-sig", dtype={"prefecture_code": str})
    iso = pd.read_csv(ISO_FILE, encoding="utf-8-sig", dtype={"prefecture_code": str})
    sec = pd.read_csv(SEC_FILE, encoding="utf-8-sig", dtype={"prefecture_code": str})
    cov = pd.read_csv(COV_FILE, encoding="utf-8-sig", dtype={"prefecture_code": str})

    print(f"BZ処方: {bz.shape},  独居老人率: {iso.shape}")
    print(f"副アウトカム: {sec.shape},  共変量: {cov.shape}")

    # ----------------------------------------------------------
    # 2. 順次結合
    # ----------------------------------------------------------
    df = pd.merge(bz, iso[["prefecture_code",
                            "solo_65plus_households", "pop_65plus",
                            "solo_elderly_rate"]],
                  on="prefecture_code", how="inner")
    df = pd.merge(df, sec[["prefecture_code",
                            "homecare_patients", "psychiatry_patients"]],
                  on="prefecture_code", how="inner")
    df = pd.merge(df, cov[["prefecture_code", "prefecture_name",
                            "population", "aging_rate", "pop_density",
                            "income_per_capita", "pa_rate_permil"]],
                  on="prefecture_code", how="inner", suffixes=("_bz", ""))
    df = df.drop(columns=["prefecture_name_bz"], errors="ignore")

    print(f"\n結合後: {df.shape}  (都道府県数: {len(df)})")
    if len(df) != 47:
        print("[WARNING] 47都道府県に満たない！マッピングを確認してください。")

    # ----------------------------------------------------------
    # 3. アウトカム変数を計算
    # ----------------------------------------------------------
    # 主アウトカム: 外来（院外+院内）処方量 / 人口10万人
    df["bz_count_outpatient"] = (df["bz_count_outpatient_ext"]
                                 + df["bz_count_outpatient_int"])
    df["bz_drug_rate"]     = df["bz_count_outpatient"] / df["population"] * 100_000
    df["bz_drug_rate_all"] = df["bz_count_total"]      / df["population"] * 100_000

    # 対数変換（感度分析Spec5用）
    df["log_bz_drug_rate"]     = np.log(df["bz_drug_rate"].clip(lower=0.01))
    df["log_bz_drug_rate_all"] = np.log(df["bz_drug_rate_all"].clip(lower=0.01))

    # 副アウトカム
    # 在宅医療: 65歳以上人口10,000人あたり（高齢者特有の医療サービス）
    df["homecare_rate"] = df["homecare_patients"] / df["pop_65plus"] * 10_000
    # 精神科専門療法料: 人口10万人あたり
    df["psychiatry_rate"] = df["psychiatry_patients"] / df["population"] * 100_000

    # ----------------------------------------------------------
    # 4. 記述統計
    # ----------------------------------------------------------
    key_cols = ["bz_drug_rate", "solo_elderly_rate",
                "homecare_rate", "psychiatry_rate",
                "aging_rate", "pop_density", "income_per_capita"]

    print(f"\n記述統計 (N=47):")
    print(df[key_cols].describe().round(2).to_string())

    print(f"\n相関行列（主要変数）:")
    print(df[key_cols].corr().round(3).to_string())

    # ----------------------------------------------------------
    # 5. 保存
    # ----------------------------------------------------------
    cols_out = [
        "prefecture_code", "prefecture_name",
        "population", "aging_rate", "pop_density",
        "income_per_capita", "pa_rate_permil",
        "solo_65plus_households", "pop_65plus", "solo_elderly_rate",
        "bz_count_outpatient_ext", "bz_count_outpatient_int",
        "bz_count_inpatient", "bz_count_total", "bz_count_outpatient",
        "bz_drug_rate", "bz_drug_rate_all",
        "log_bz_drug_rate", "log_bz_drug_rate_all",
        "homecare_patients", "homecare_rate",
        "psychiatry_patients", "psychiatry_rate",
    ]
    df[cols_out].to_csv(OUT_FILE, index=False, encoding="utf-8-sig")
    print(f"\n[保存] {OUT_FILE}")
    print(f"  変数数: {len(cols_out)}, 行数: {len(df)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
