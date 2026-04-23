# -*- coding: utf-8 -*-
"""
02_fetch_census_isolation.py
2020年国勢調査メッシュデータから都道府県別「65歳以上独居老人率」を集計する。

独居老人率 = 高齢単身世帯数 / 65歳以上人口

データソース:
  02_Data/raw/Statistics_Bureau/Census_2020/tblT001141H{NN}.txt
  （e-Stat 国勢調査 小地域集計 テーブルT001141, 都道府県別ファイル NN=01-47）

使用カラム（ヘッダー行のラベルで確認済み）:
  T001141019: 65歳以上人口（総数）
  T001141049: 高齢単身世帯数（一般世帯数）= 65歳以上単独世帯数

出力:
  03_Analysis/results/census_isolation.csv
    prefecture_code, prefecture_name, solo_65plus_households, pop_65plus,
    solo_elderly_rate
"""

from pathlib import Path
import pandas as pd
import yaml

SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_DIR  = SCRIPT_DIR.parents[1]
PROJECT_ROOT = SCRIPT_DIR.parents[3]
CONFIG_FILE  = PROJECT_DIR / "config" / "config.yaml"
OUT_DIR      = SCRIPT_DIR.parent / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE     = OUT_DIR / "census_isolation.csv"

CENSUS_DIR = (PROJECT_ROOT / "02_Data" / "raw"
              / "Statistics_Bureau" / "Census_2020")

COL_POP65   = "T001141019"   # 65歳以上人口（総数）
COL_SOLO65  = "T001141049"   # 高齢単身世帯数（一般世帯数）

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


def load_config():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_prefecture_file(pref_code: str) -> dict:
    """
    tblT001141H{NN}.txt を読み込み、COL_POP65 と COL_SOLO65 の都道府県合計を返す。
    ファイル構造:
      行0: ヘッダー名（英語コード）
      行1: カラムラベル（日本語）
      行2以降: 小地域メッシュデータ
    """
    fname = CENSUS_DIR / f"tblT001141H{pref_code}.txt"
    if not fname.exists():
        raise FileNotFoundError(f"国勢調査ファイルが見つかりません: {fname}")

    # 行0=英語コードヘッダー, 行1=日本語ラベル（スキップ）, 行2以降=データ
    df = pd.read_csv(fname, encoding="cp932", header=0, skiprows=[1],
                     dtype={"KEY_CODE": str}, low_memory=False)

    for col in [COL_POP65, COL_SOLO65]:
        if col not in df.columns:
            raise KeyError(f"{col} が {fname.name} に存在しません")

    df[COL_POP65]  = pd.to_numeric(df[COL_POP65],  errors="coerce")
    df[COL_SOLO65] = pd.to_numeric(df[COL_SOLO65], errors="coerce")

    return {
        "pop_65plus":            int(df[COL_POP65].sum()),
        "solo_65plus_households": int(df[COL_SOLO65].sum()),
    }


def main():
    print("=" * 60)
    print(" 02_fetch_census_isolation.py  独居老人率取得（実データ）")
    print("=" * 60)
    print(f"  データソース: {CENSUS_DIR}")
    print(f"  カラム: {COL_POP65}(65歳以上人口) / {COL_SOLO65}(高齢単身世帯数)")

    rows = []
    for code, name in zip(PREF_CODES, PREF_NAMES):
        vals = read_prefecture_file(code)
        rate = vals["solo_65plus_households"] / vals["pop_65plus"]
        rows.append({
            "prefecture_code":        code,
            "prefecture_name":        name,
            "solo_65plus_households": vals["solo_65plus_households"],
            "pop_65plus":             vals["pop_65plus"],
            "solo_elderly_rate":      round(rate, 6),
        })
        print(f"  [{code}] {name:6s}: 高齢単身={vals['solo_65plus_households']:>8,}  "
              f"65歳以上人口={vals['pop_65plus']:>9,}  率={rate:.4f}")

    df = pd.DataFrame(rows)

    print(f"\n[検証] 都道府県数: {len(df)}")
    print(f"[検証] 欠損値: {df.isnull().sum().sum()}")
    rate_min = df["solo_elderly_rate"].min()
    rate_max = df["solo_elderly_rate"].max()
    print(f"[検証] 独居老人率の範囲: {rate_min:.4f} 〜 {rate_max:.4f}")
    if not (0.05 <= rate_min and rate_max <= 0.45):
        print("  [WARNING] 独居老人率の範囲が想定外（0.05〜0.45）。データを確認してください。")

    print("\n記述統計（独居老人率）:")
    print(df["solo_elderly_rate"].describe().round(4).to_string())

    df.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")

    # キャッシュも更新
    cfg = load_config()
    cache_file = PROJECT_DIR / cfg["estat"]["census_cache_file"]
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache_file, index=False, encoding="utf-8-sig")

    print(f"\n[保存] {OUT_FILE}")
    print(f"[キャッシュ保存] {cache_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
