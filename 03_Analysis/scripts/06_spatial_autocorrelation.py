# -*- coding: utf-8 -*-
"""
06_spatial_autocorrelation.py
Global Moran's I + LISA クラスタ分析を実行する。

転用元: projects/NDB_XXX_poverty_tgi/03_Analysis/scripts/05_spatial_autocorrelation.py
変更点: 対象変数をBZ系・独居老人率・副アウトカムに変更

出力:
  03_Analysis/results/moran_results.csv     Global Moran's I
  03_Analysis/results/lisa_results.csv      LISA クラスタラベル
  03_Analysis/results/lisa_cluster_map.png  LISA クラスタ地図（bz_drug_rate）
"""

from pathlib import Path
import warnings
import yaml
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd
import libpysal
from esda.moran import Moran, Moran_Local

warnings.filterwarnings("ignore")

SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_DIR  = SCRIPT_DIR.parents[1]
PROJECT_ROOT = SCRIPT_DIR.parents[3]
CONFIG_FILE  = PROJECT_DIR / "config" / "config.yaml"
RESULTS_DIR  = SCRIPT_DIR.parent / "results"
DATA_FILE    = RESULTS_DIR / "analysis_dataset.csv"
GEO_FILE     = PROJECT_ROOT / "02_Data" / "raw" / "GIS" / "japan.geojson"


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
CODE_TO_NAME = dict(zip(PREF_CODES, PREF_NAMES))


def load_geodataframe(df: pd.DataFrame) -> gpd.GeoDataFrame:
    """GeoJSONを読み込みデータと結合してGeoDataFrameを返す"""
    gdf = gpd.read_file(GEO_FILE)
    name_col = "nam_ja" if "nam_ja" in gdf.columns else "nam"
    name_to_code = {v: k for k, v in CODE_TO_NAME.items()}
    gdf["prefecture_code"] = gdf[name_col].map(name_to_code)
    gdf = gdf.dropna(subset=["prefecture_code"])
    merged = gdf.merge(df, on="prefecture_code", how="inner")
    print(f"  GeoJSON結合後: {len(merged)}都道府県")
    return merged


def build_weights(gdf: gpd.GeoDataFrame) -> libpysal.weights.W:
    """Queen隣接重み行列を構築（沖縄などの離島はKNN補完）"""
    w = libpysal.weights.Queen.from_dataframe(gdf)

    if w.islands:
        print(f"  [INFO] 孤立ノード検出: {len(w.islands)}個（KNN=2 で補完）")
        w_knn = libpysal.weights.KNN.from_dataframe(gdf, k=2)
        for island in w.islands:
            for neighbor in w_knn.neighbors[island]:
                w.neighbors[island].append(neighbor)
                w.neighbors[neighbor].append(island)
        w = libpysal.weights.W(w.neighbors, silence_warnings=True)

    w.transform = "r"  # row standardize
    return w


def main():
    print("=" * 60)
    print(" 06_spatial_autocorrelation.py  空間自己相関")
    print("=" * 60)

    cfg = load_config()
    spatial_cfg = cfg["analysis"]["spatial"]
    target_vars = spatial_cfg["target_vars"]
    permutations = spatial_cfg["permutations"]

    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig",
                     dtype={"prefecture_code": str})

    if not GEO_FILE.exists():
        print(f"[ERROR] GeoJSONが見つかりません: {GEO_FILE}")
        return

    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from ndb_library.viz import set_japanese_font
    set_japanese_font()

    gdf = load_geodataframe(df)
    w   = build_weights(gdf)

    moran_rows = []
    lisa_rows  = []

    for var in target_vars:
        if var not in gdf.columns:
            print(f"  [SKIP] {var} が GeoDataFrame に存在しません")
            continue

        y = gdf[var].values.astype(float)

        # Global Moran's I
        mi = Moran(y, w, permutations=permutations)
        sig_str = ("***" if mi.p_sim < 0.001 else
                   ("**"  if mi.p_sim < 0.01  else
                    ("*"   if mi.p_sim < 0.05  else "ns")))
        moran_rows.append({
            "variable": var,
            "moran_I":  round(mi.I,     4),
            "p_value":  round(mi.p_sim, 4),
            "z_score":  round(mi.z_sim, 4),
            "EI":       round(mi.EI,    4),
        })
        print(f"\n[Global Moran's I] {var}")
        print(f"  I = {mi.I:.4f},  p = {mi.p_sim:.4f} {sig_str}")

        # Local Moran's I (LISA)
        lisa = Moran_Local(y, w, permutations=permutations)
        labels = []
        for i in range(len(gdf)):
            if lisa.p_sim[i] < 0.05:
                q = lisa.q[i]
                label = {1: "HH", 2: "LH", 3: "LL", 4: "HL"}.get(q, "ns")
            else:
                label = "ns"
            labels.append(label)
        gdf[f"lisa_{var}"] = labels

        for idx, (i, row) in enumerate(gdf.iterrows()):
            lisa_rows.append({
                "prefecture_code": row["prefecture_code"],
                "prefecture_name": row.get("prefecture_name", ""),
                "variable":        var,
                "lisa_cluster":    labels[idx],
                "Is":              round(float(lisa.Is[idx]),     4),
                "p_sim":           round(float(lisa.p_sim[idx]),  4),
            })

    # --------------------------------------------------------
    # LISA クラスタ地図（bz_drug_rate）
    # --------------------------------------------------------
    primary_var = cfg["analysis"]["outcome_primary"]
    lisa_col    = f"lisa_{primary_var}"

    if lisa_col in gdf.columns:
        color_map = {
            "HH": "#d7191c",
            "HL": "#fdae61",
            "LH": "#abd9e9",
            "LL": "#2c7bb6",
            "ns": "#f0f0f0",
        }
        fig, ax = plt.subplots(1, 1, figsize=(10, 9))
        gdf["color"] = gdf[lisa_col].map(color_map)
        gdf.plot(color=gdf["color"], ax=ax, edgecolor="white", linewidth=0.4)

        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor="#d7191c", label="High-High Cluster"),
            Patch(facecolor="#fdae61", label="High-Low Outlier"),
            Patch(facecolor="#abd9e9", label="Low-High Outlier"),
            Patch(facecolor="#2c7bb6", label="Low-Low Cluster"),
            Patch(facecolor="#f0f0f0", label="Not Significant"),
        ]
        ax.legend(handles=legend_elements, loc="lower left", fontsize=9)
        ax.set_title(
            "Figure 5. LISA Cluster Map\nBZ Drug Prescription Rate (Prefecture-Level, FY2023)",
            fontsize=13, pad=12)
        ax.axis("off")
        plt.tight_layout()
        plt.savefig(RESULTS_DIR / "lisa_cluster_map.png", dpi=300)
        plt.close()
        print(f"\n[保存] lisa_cluster_map.png")

    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------
    pd.DataFrame(moran_rows).to_csv(
        RESULTS_DIR / "moran_results.csv",
        index=False, encoding="utf-8-sig")
    pd.DataFrame(lisa_rows).to_csv(
        RESULTS_DIR / "lisa_results.csv",
        index=False, encoding="utf-8-sig")
    print(f"[保存] moran_results.csv, lisa_results.csv")
    print("=" * 60)


if __name__ == "__main__":
    main()
