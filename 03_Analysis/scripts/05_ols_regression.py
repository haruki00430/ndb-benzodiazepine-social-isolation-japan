# -*- coding: utf-8 -*-
"""
05_ols_regression.py
OLS回帰（主解析）+ HC3 robust SE + 感度分析6仕様 + 副アウトカム解析を実行する。

転用元: projects/NDB_XXX_poverty_tgi/03_Analysis/scripts/04_ols_regression.py
変更点: 主説明変数を pa_rate_permil → solo_elderly_rate に変更

主解析モデル:
  bz_drug_rate ~ solo_elderly_rate + aging_rate + pop_density + income_per_capita (HC3)

感度分析6仕様:
  Spec1_Baseline        : 標準OLS (nonrobust)
  Spec2_HC3             : HC3 robust SE（主解析）
  Spec3_OutlierRemoved  : ±2SD 除外
  Spec4_NoBig3          : 東京・大阪・愛知除外
  Spec5_LogY            : log(bz_drug_rate) を従属変数
  Spec6_Interaction     : solo_elderly_rate × income_per_capita 交互作用項

副アウトカム: homecare_rate, psychiatry_rate でも同モデルを実行

出力:
  03_Analysis/results/regression_main.csv
  03_Analysis/results/sensitivity_analysis.csv
  03_Analysis/results/vif_results.csv
  03_Analysis/results/table1_descriptive.csv
  03_Analysis/results/secondary_regression.csv
"""

from pathlib import Path
import warnings
import yaml
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

warnings.filterwarnings("ignore")

SCRIPT_DIR  = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parents[1]
CONFIG_FILE = PROJECT_DIR / "config" / "config.yaml"
RESULTS_DIR = SCRIPT_DIR.parent / "results"
DATA_FILE   = RESULTS_DIR / "analysis_dataset.csv"


def load_config():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def fit_ols(df: pd.DataFrame, y_col: str, x_cols: list,
            robust: str = "HC3") -> tuple[list, object]:
    """OLS + robust SE を実行して結果辞書のリストとモデルを返す"""
    y = df[y_col]
    X = sm.add_constant(df[x_cols])
    model = sm.OLS(y, X).fit(cov_type=robust)
    rows = []
    for var in x_cols:
        rows.append({
            "variable": var,
            "beta":     model.params[var],
            "se":       model.bse[var],
            "t":        model.tvalues[var],
            "p":        model.pvalues[var],
            "ci_lo":    model.conf_int().loc[var, 0],
            "ci_hi":    model.conf_int().loc[var, 1],
            "r2":       model.rsquared,
            "r2_adj":   model.rsquared_adj,
            "n":        int(model.nobs),
        })
    return rows, model


def calc_vif(df: pd.DataFrame, x_cols: list) -> pd.DataFrame:
    X = sm.add_constant(df[x_cols]).astype(float)
    return pd.DataFrame({
        "variable": x_cols,
        "VIF": [variance_inflation_factor(X.values, i + 1)
                for i in range(len(x_cols))]
    })


def robustness_summary(sens_df: pd.DataFrame, var_col: str, var_name: str):
    """感度分析の頑健性サマリを表示"""
    sub = sens_df[sens_df["variable"] == var_col].copy()
    sub["sig_p05"] = sub["p"] < 0.05
    n_sig   = sub["sig_p05"].sum()
    n_total = len(sub)
    print(f"\n{'='*40}")
    print(f" 感度分析 サマリ ({var_name})")
    print(f"{'='*40}")
    print(sub[["spec", "beta", "se", "p", "sig_p05"]].to_string(index=False))
    label = ("頑健（5/6以上有意）"  if n_sig >= 5 else
             "中程度（3-4/6有意）"  if n_sig >= 3 else
             "不安定（2/6以下有意）")
    print(f"\n→ 頑健性: {n_sig}/{n_total} 仕様で p<0.05  [{label}]")


def main():
    print("=" * 60)
    print(" 05_ols_regression.py  回帰分析")
    print("=" * 60)

    cfg = load_config()
    analysis = cfg["analysis"]

    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig",
                     dtype={"prefecture_code": str})
    print(f"データ読み込み: N={len(df)}")

    Y       = analysis["outcome_primary"]   # "bz_drug_rate"
    LOG_Y   = analysis["outcome_log"]       # "log_bz_drug_rate"
    EXPO    = analysis["exposure_main"]     # "solo_elderly_rate"
    AGING   = analysis["covariates"][0]     # "aging_rate"
    DENSITY = analysis["covariates"][1]     # "pop_density"
    INC     = analysis["covariates"][2]     # "income_per_capita"
    BIG3    = analysis["big3_prefectures"]  # ["13","27","23"]

    main_x = [EXPO, AGING, DENSITY, INC]

    # --------------------------------------------------------
    # Table 1: 記述統計
    # --------------------------------------------------------
    t1_cols = [Y, EXPO, AGING, DENSITY, INC, "pa_rate_permil",
               "homecare_rate", "psychiatry_rate"]
    t1 = df[t1_cols].describe().T.round(2)
    t1.columns = ["count", "mean", "sd", "min", "p25", "p50", "p75", "max"]
    t1.to_csv(RESULTS_DIR / "table1_descriptive.csv", encoding="utf-8-sig")
    print("\nTable 1 記述統計:")
    print(t1.to_string())

    # --------------------------------------------------------
    # VIF（多重共線性チェック）
    # --------------------------------------------------------
    vif_df = calc_vif(df, main_x)
    vif_df.to_csv(RESULTS_DIR / "vif_results.csv",
                  index=False, encoding="utf-8-sig")
    print(f"\nVIF:")
    print(vif_df.to_string(index=False))
    if (vif_df["VIF"] > 10).any():
        print("  [WARNING] VIF > 10 の変数があります。多重共線性を確認してください。")

    # --------------------------------------------------------
    # 主解析: bz_drug_rate ~ solo_elderly_rate + aging_rate + pop_density + income (HC3)
    # --------------------------------------------------------
    print(f"\n{'='*40}")
    print(" 主解析 (HC3 robust SE)")
    print("=" * 40)
    main_rows, main_model = fit_ols(df, Y, main_x)
    print(main_model.summary())

    # --------------------------------------------------------
    # 感度分析6仕様
    # --------------------------------------------------------
    specs = {}

    # Spec1: Baseline OLS（nonrobust）
    specs["Spec1_Baseline"]       = fit_ols(df, Y, main_x, robust="nonrobust")[0]
    # Spec2: HC3 robust SE（主解析）
    specs["Spec2_HC3"]            = main_rows
    # Spec3: 外れ値除外（±2SD）
    z = (df[Y] - df[Y].mean()) / df[Y].std()
    df_no_outlier = df[np.abs(z) <= 2].copy()
    specs["Spec3_OutlierRemoved"] = fit_ols(df_no_outlier, Y, main_x)[0]
    # Spec4: 大都市3都市除外
    df_no_big3 = df[~df["prefecture_code"].isin(BIG3)].copy()
    specs["Spec4_NoBig3"]         = fit_ols(df_no_big3, Y, main_x)[0]
    # Spec5: 対数変換 Y
    specs["Spec5_LogY"]           = fit_ols(df, LOG_Y, main_x)[0]
    # Spec6: 交互作用項（独居老人率 × 所得）
    df["iso_inc_interact"] = df[EXPO] * df[INC]
    interact_x = main_x + ["iso_inc_interact"]
    specs["Spec6_Interaction"]    = fit_ols(df, Y, interact_x)[0]

    # 感度分析結果を整形
    rows_all = []
    for spec_name, rows in specs.items():
        for r in rows:
            r["spec"] = spec_name
            rows_all.append(r)
    sens_df = pd.DataFrame(rows_all)[
        ["spec", "variable", "beta", "se", "t", "p",
         "ci_lo", "ci_hi", "r2", "r2_adj", "n"]
    ]

    robustness_summary(sens_df, EXPO, "solo_elderly_rate")
    robustness_summary(sens_df, AGING, "aging_rate")

    # --------------------------------------------------------
    # 副アウトカム解析
    # --------------------------------------------------------
    print(f"\n{'='*40}")
    print(" 副アウトカム解析")
    print("=" * 40)

    sec_rows_all = []
    for sec_y in analysis["secondary_outcomes"]:
        if sec_y not in df.columns:
            print(f"  [SKIP] {sec_y} が analysis_dataset.csv に存在しません")
            continue
        rows_sec, model_sec = fit_ols(df, sec_y, main_x)
        for r in rows_sec:
            r["outcome"] = sec_y
        sec_rows_all.extend(rows_sec)
        print(f"\n[{sec_y}]  R2={model_sec.rsquared:.3f},  n={int(model_sec.nobs)}")
        for r in rows_sec:
            sig = "*" if r["p"] < 0.05 else ("+" if r["p"] < 0.10 else "")
            print(f"  {r['variable']:25s}  b={r['beta']:10.4f}  p={r['p']:.4f} {sig}")

    sec_df = pd.DataFrame(sec_rows_all)
    if not sec_df.empty:
        sec_df = sec_df[["outcome", "variable", "beta", "se", "t", "p",
                          "ci_lo", "ci_hi", "r2", "r2_adj", "n"]]
        sec_df.to_csv(RESULTS_DIR / "secondary_regression.csv",
                      index=False, encoding="utf-8-sig")
        print(f"\n[保存] secondary_regression.csv")

    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------
    sens_df.to_csv(RESULTS_DIR / "sensitivity_analysis.csv",
                   index=False, encoding="utf-8-sig")
    pd.DataFrame(main_rows).to_csv(
        RESULTS_DIR / "regression_main.csv",
        index=False, encoding="utf-8-sig")

    print(f"\n[保存] regression_main.csv, sensitivity_analysis.csv, vif_results.csv")
    print("=" * 60)


if __name__ == "__main__":
    main()
