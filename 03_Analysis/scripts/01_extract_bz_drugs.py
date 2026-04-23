# -*- coding: utf-8 -*-
"""
01_extract_bz_drugs.py
NDB No.10（FY2023）からBZ系薬剤（薬効分類コード112+117）の
都道府県別処方量を抽出する。

転用元: projects/NDB_XXX_poverty_tgi/03_Analysis/scripts/01_extract_ndb396.py
変更点: TARGET_CODE="396" → TARGET_CODES=["112","117"]（configから読み込み）

入力:
  02_Data/raw/NDB_OpenData/No.10/05_処方薬/.../
    【内服】外来（院外）_都道府県別薬効分類別数量.xlsx
    【内服】外来（院内）_都道府県別薬効分類別数量.xlsx
    【内服】入院_都道府県別薬効分類別数量.xlsx

出力:
  03_Analysis/results/bz_prefecture.csv
    prefecture_code, prefecture_name, bz_count_outpatient_ext,
    bz_count_outpatient_int, bz_count_inpatient, bz_count_total
"""

import sys
from pathlib import Path
import yaml
import pandas as pd
import numpy as np

# パス設定
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_DIR  = SCRIPT_DIR.parents[1]  # NDB_XXX_social_isolation_bz/
PROJECT_ROOT = SCRIPT_DIR.parents[3]  # NDB_Research_Hub/
CONFIG_FILE  = PROJECT_DIR / "config" / "config.yaml"
OUT_DIR      = SCRIPT_DIR.parent / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE     = OUT_DIR / "bz_prefecture.csv"


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
    """全角数字・マスク値（"−","－","-"）→ NaN → 0 に変換"""
    s = series.astype(str).str.strip()
    s = s.str.translate(str.maketrans("０１２３４５６７８９．", "0123456789."))
    s = s.replace({"−": np.nan, "-": np.nan, "－": np.nan, "": np.nan})
    return pd.to_numeric(s, errors="coerce").fillna(0)


def extract_bz_codes(filepath: Path, label: str, target_codes: list,
                     header_row: int, pref_col_start: int) -> pd.Series:
    """指定ファイルからBZ系コードの都道府県別合計処方量を返す（index=都道府県コード）"""
    print(f"  読み込み中: {filepath.name}")
    if not filepath.exists():
        print(f"    [ERROR] ファイルが見つかりません: {filepath}")
        sys.exit(1)

    # データ本体（行 header_row+2 以降）
    df = pd.read_excel(filepath, header=None, skiprows=header_row + 2, dtype=str)

    n_cols = len(df.columns)
    if n_cols < pref_col_start + 47:
        print(f"    [WARNING] 列数が想定未満: {n_cols}")

    # 列0 = 薬効コード（グループ先頭のみ記載, 以降NaN）→ ffill 必須
    df.iloc[:, 0] = df.iloc[:, 0].ffill()

    # BZ系コード（112, 117）の行を抽出
    mask = (df.iloc[:, 0]
            .astype(str).str.strip()
            .str.split(".").str[0]
            .isin(target_codes))
    df_bz = df[mask].copy()

    if df_bz.empty:
        print(f"    [WARNING] コード{target_codes}の行が見つかりませんでした")
        return pd.Series(0.0, index=PREF_CODES, name=label)

    print(f"    コード{target_codes} 品目数: {len(df_bz)}")

    # 都道府県列（pref_col_start〜pref_col_start+47）の数値化と合計
    pref_cols = list(range(pref_col_start, pref_col_start + 47))
    df_bz_pref = df_bz.iloc[:, pref_cols].copy()

    for c in df_bz_pref.columns:
        df_bz_pref[c] = to_numeric_col(df_bz_pref[c])

    totals = df_bz_pref.sum(axis=0).values  # shape (47,)
    result = pd.Series(totals, index=PREF_CODES, name=label)
    print(f"    全国合計処方量: {result.sum():,.0f}")
    return result


def main():
    print("=" * 60)
    print(" 01_extract_bz_drugs.py  BZ系薬剤（112+117）抽出")
    print("=" * 60)

    cfg = load_config()
    target_codes  = cfg["bz_drugs"]["drug_effect_codes"]
    header_row    = cfg["bz_drugs"]["header_row"]
    pref_col_start = cfg["bz_drugs"]["pref_col_start"]
    pref_col_end   = cfg["bz_drugs"]["pref_col_end"]

    NDB_DIR = (PROJECT_ROOT / "02_Data" / "raw" / "NDB_OpenData" / "No.10"
               / "05_処方薬" / "01_公費レセプトを含まないデータ"
               / "01_処方薬（内服／外用／注射）")

    target_files = cfg["bz_drugs"]["target_files"]
    FILES = {
        "outpatient_ext": NDB_DIR / target_files["outpatient_ext"],
        "outpatient_int": NDB_DIR / target_files["outpatient_int"],
        "inpatient":      NDB_DIR / target_files["inpatient"],
    }

    col_labels = {
        "outpatient_ext": "bz_count_outpatient_ext",
        "outpatient_int": "bz_count_outpatient_int",
        "inpatient":      "bz_count_inpatient",
    }

    series_list = []
    for key, filepath in FILES.items():
        label = col_labels[key]
        s = extract_bz_codes(filepath, label, target_codes,
                              header_row, pref_col_start)
        series_list.append(s)

    # 結合
    df_out = pd.DataFrame(series_list).T
    df_out.index.name = "prefecture_code"
    df_out = df_out.reset_index()
    df_out["prefecture_name"] = PREF_NAMES
    df_out["bz_count_total"] = (
        df_out["bz_count_outpatient_ext"]
        + df_out["bz_count_outpatient_int"]
        + df_out["bz_count_inpatient"]
    )

    df_out = df_out[[
        "prefecture_code", "prefecture_name",
        "bz_count_outpatient_ext", "bz_count_outpatient_int",
        "bz_count_inpatient", "bz_count_total",
    ]]

    print(f"\n[検証] 都道府県数: {len(df_out)}")
    print(f"[検証] 欠損値: {df_out.isnull().sum().sum()}")
    print(f"[検証] 処方量ゼロ都道府県: {(df_out['bz_count_total'] == 0).sum()}")
    print("\nサンプル（先頭5件）:")
    print(df_out.head().to_string(index=False))

    df_out.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")
    print(f"\n[保存] {OUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
