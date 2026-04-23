# -*- coding: utf-8 -*-
"""
03_load_secondary_outcomes.py
NDB No.10（FY2023）から副アウトカムを抽出する。

副アウトカム:
  - C_在宅医療:       都道府県別患者数合計
  - I_精神科専門療法料: 都道府県別患者数合計

注意: 医科診療行為Excelの列位置は処方薬と異なる（pref_col_start=6）

入力:
  01_医科診療行為（患者数）/.../C_在宅医療/都道府県別患者数.xlsx
  01_医科診療行為（患者数）/.../I_精神科専門療法料/都道府県別患者数.xlsx

出力:
  03_Analysis/results/secondary_outcomes.csv
    prefecture_code, prefecture_name, homecare_patients, psychiatry_patients
"""

import sys
from pathlib import Path
import yaml
import pandas as pd
import numpy as np

# パス設定
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_DIR  = SCRIPT_DIR.parents[1]
PROJECT_ROOT = SCRIPT_DIR.parents[3]
CONFIG_FILE  = PROJECT_DIR / "config" / "config.yaml"
OUT_DIR      = SCRIPT_DIR.parent / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE     = OUT_DIR / "secondary_outcomes.csv"


def load_config():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


PREF_NAMES = [
    "北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県",
    "茨城県","栃木県","群馬県","埼玉県","千葉県","東京都","神奈川県",
    "新潟県","富山県","石川県","福井県","山梨県","長野県",
    "岐阜県","静岡県","愛知県","三重県",
    "滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県",
    "鳥取県","島根県","岡山県","広島県","山口県",
    "徳島県","香川県","愛媛県","高知県",
    "福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県",
]
PREF_CODES = [f"{i:02d}" for i in range(1, 48)]


def to_numeric_col(series: pd.Series) -> pd.Series:
    """全角数字・マスク値 → NaN → 0"""
    s = series.astype(str).str.strip()
    s = s.str.translate(str.maketrans("０１２３４５６７８９．", "0123456789."))
    s = s.replace({"−": np.nan, "-": np.nan, "－": np.nan, "": np.nan})
    return pd.to_numeric(s, errors="coerce").fillna(0)


def extract_medical_acts_total(filepath: Path, label: str,
                               header_row: int, pref_col_start: int) -> pd.Series:
    """
    医科診療行為Excelから全診療行為コードの都道府県別患者数合計を返す。

    ファイル構造:
      行0: タイトル
      行1: 空白
      行2: ヘッダー（分類コード/分類名/診療行為コード/診療行為名/点数/全国合計/01〜47）
      行3: 都道府県名
      行4〜: データ（分類コードは先頭行のみ → ffill 必要）
    """
    print(f"  読み込み中: {filepath.name}")
    if not filepath.exists():
        print(f"    [ERROR] ファイルが見つかりません: {filepath}")
        sys.exit(1)

    # データ本体（行 header_row+2 以降）
    df = pd.read_excel(filepath, header=None, skiprows=header_row + 2, dtype=str)

    n_cols = len(df.columns)
    expected_min = pref_col_start + 47
    if n_cols < expected_min:
        print(f"    [WARNING] 列数が想定未満: {n_cols} < {expected_min}")

    # 列0 = 分類コード（グループ先頭のみ記載）→ ffill
    df.iloc[:, 0] = df.iloc[:, 0].ffill()

    # 都道府県列（pref_col_start〜pref_col_start+47）の数値化と合計
    pref_cols = list(range(pref_col_start, pref_col_start + 47))
    df_pref = df.iloc[:, pref_cols].copy()

    for c in df_pref.columns:
        df_pref[c] = to_numeric_col(df_pref[c])

    totals = df_pref.sum(axis=0).values  # 全診療行為の合計
    result = pd.Series(totals, index=PREF_CODES, name=label)
    print(f"    全国合計患者数: {result.sum():,.0f}")
    return result


def main():
    print("=" * 60)
    print(" 03_load_secondary_outcomes.py  副アウトカム抽出")
    print("=" * 60)

    cfg = load_config()
    sec = cfg["secondary_outcomes"]
    header_row    = sec["header_row"]
    pref_col_start = sec["pref_col_start"]

    NDB_DIR = (PROJECT_ROOT / "02_Data" / "raw" / "NDB_OpenData" / "No.10"
               / "01_医科診療行為（患者数）" / "01_公費レセプトを含まないデータ")

    homecare_file  = NDB_DIR / sec["homecare"]["section_label"]   / sec["homecare"]["filename"]
    psychiatry_file = NDB_DIR / sec["psychiatry"]["section_label"] / sec["psychiatry"]["filename"]

    print("\n[C_在宅医療 患者数]")
    s_homecare = extract_medical_acts_total(
        homecare_file, sec["homecare"]["output_col"],
        header_row, pref_col_start)

    print("\n[I_精神科専門療法料 患者数]")
    s_psychiatry = extract_medical_acts_total(
        psychiatry_file, sec["psychiatry"]["output_col"],
        header_row, pref_col_start)

    # 結合
    df_out = pd.DataFrame({
        "prefecture_code":   PREF_CODES,
        "prefecture_name":   PREF_NAMES,
        "homecare_patients":   s_homecare.values,
        "psychiatry_patients": s_psychiatry.values,
    })

    print(f"\n[検証] 都道府県数: {len(df_out)}")
    print(f"[検証] 欠損値: {df_out.isnull().sum().sum()}")
    print(f"[検証] 在宅医療患者数ゼロ都道府県: {(df_out['homecare_patients'] == 0).sum()}")
    print(f"[検証] 精神科患者数ゼロ都道府県: {(df_out['psychiatry_patients'] == 0).sum()}")
    print("\nサンプル（先頭5件）:")
    print(df_out.head().to_string(index=False))

    df_out.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")
    print(f"\n[保存] {OUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
