# -*- coding: utf-8 -*-
"""
07_visualization.py
論文用図（Figure 1-4）を作成する。

転用元: projects/NDB_XXX_poverty_tgi/03_Analysis/scripts/06_visualization.py
変更点: 変数名・タイトルをBZ系・独居老人率に対応

Figure 1: Choropleth map (bz_drug_rate)
Figure 2: Forest plot (感度分析 solo_elderly_rate)
Figure 3: Scatter plots (bz_drug_rate vs 独居老人率 / aging_rate / income)
Figure 4: Moran scatter plot (bz_drug_rate)

出力: 03_Analysis/results/*.png (300 dpi)
"""

import sys
from pathlib import Path
import warnings
import yaml
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import geopandas as gpd

warnings.filterwarnings("ignore")

SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_DIR  = SCRIPT_DIR.parents[1]
PROJECT_ROOT = SCRIPT_DIR.parents[3]
CONFIG_FILE  = PROJECT_DIR / "config" / "config.yaml"
RESULTS_DIR  = SCRIPT_DIR.parent / "results"
DATA_FILE    = RESULTS_DIR / "analysis_dataset.csv"
SENS_FILE    = RESULTS_DIR / "sensitivity_analysis.csv"
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


def load_merged_gdf(df: pd.DataFrame) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(GEO_FILE)
    name_col = "nam_ja" if "nam_ja" in gdf.columns else "nam"
    name_to_code = {v: k for k, v in CODE_TO_NAME.items()}
    gdf["prefecture_code"] = gdf[name_col].map(name_to_code)
    gdf = gdf.dropna(subset=["prefecture_code"])
    return gdf.merge(df, on="prefecture_code", how="inner")


def fig1_choropleth(df: pd.DataFrame, gdf: gpd.GeoDataFrame, cfg: dict):
    """Figure 1: BZ処方率のコロプレス図"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 9))
    cmap = cfg["visualization"]["colormap_choropleth"]
    gdf.plot(column="bz_drug_rate", ax=ax,
             cmap=cmap, legend=True,
             legend_kwds={"label": "BZ Prescriptions per 100,000 Population", "shrink": 0.6},
             edgecolor="white", linewidth=0.4,
             missing_kwds={"color": "lightgrey"})
    ax.set_title("Figure 1. Prefectural Distribution of BZ Drug Prescription Volume\n(Drug Categories 112+117, FY2023, NDB No.10)",
                 fontsize=13, pad=12)
    ax.axis("off")
    plt.tight_layout()
    out = RESULTS_DIR / "fig1_choropleth_bz_rate.png"
    plt.savefig(out, dpi=cfg["visualization"]["dpi"])
    plt.close()
    print(f"  [OK] {out.name}")


def fig2_forest_plot(sens_df: pd.DataFrame, cfg: dict):
    """Figure 2: 感度分析6仕様の Forest plot（solo_elderly_rate）"""
    var_col = cfg["analysis"]["exposure_main"]
    sub = sens_df[sens_df["variable"] == var_col].copy()
    if sub.empty:
        print(f"  [SKIP] Figure 2: {var_col} の感度分析結果がありません")
        return
    sub["spec_label"] = sub["spec"].str.replace("Spec", "Spec ").str.replace("_", " ")

    fig, ax = plt.subplots(figsize=(9, 5))
    y_pos = list(range(len(sub)))
    for i, (_, row) in enumerate(sub.iterrows()):
        c = cfg["visualization"]["color_significant"] if row["p"] < 0.05 \
            else cfg["visualization"]["color_nonsignificant"]
        ax.errorbar(row["beta"], i,
                    xerr=[[row["beta"] - row["ci_lo"]], [row["ci_hi"] - row["beta"]]],
                    fmt="o", color=c, ecolor=c,
                    elinewidth=1.5, capsize=4, markersize=7, zorder=3)
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sub["spec_label"], fontsize=10)
    ax.set_xlabel("Regression Coefficient β (Solo Elderly Rate → BZ Prescriptions per 100,000)", fontsize=11)
    ax.set_title("Figure 2. Sensitivity Analysis Forest Plot\n(Red = p < 0.05; Grey = Non-significant)",
                 fontsize=12, pad=10)
    ax.invert_yaxis()
    plt.tight_layout()
    out = RESULTS_DIR / "fig2_forest_plot_isolation.png"
    plt.savefig(out, dpi=cfg["visualization"]["dpi"])
    plt.close()
    print(f"  [OK] {out.name}")


def fig3_scatter(df: pd.DataFrame, cfg: dict):
    """Figure 3: bz_drug_rate vs 各説明変数の散布図（3枚）"""
    pairs = [
        ("solo_elderly_rate", "Solo Elderly Rate (2020 Census)"),
        ("aging_rate",        "Aging Rate (%)"),
        ("income_per_capita", "Per Capita Prefectural Income (1,000 JPY)"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for ax, (xcol, xlabel) in zip(axes, pairs):
        ax.scatter(df[xcol], df["bz_drug_rate"],
                   color="#2c7fb8", alpha=0.7, s=50,
                   edgecolors="white", linewidths=0.5)
        m, b = np.polyfit(df[xcol], df["bz_drug_rate"], 1)
        xline = np.linspace(df[xcol].min(), df[xcol].max(), 100)
        ax.plot(xline, m * xline + b, "r--", linewidth=1.2)
        r = df[[xcol, "bz_drug_rate"]].corr().iloc[0, 1]
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_ylabel("BZ Prescriptions per 100,000 Population", fontsize=10)
        ax.set_title(f"r = {r:.3f}", fontsize=11)

    fig.suptitle("Figure 3. Scatter Plots of BZ Prescription Rate Against Explanatory Variables",
                 fontsize=13, y=1.02)
    plt.tight_layout()
    out = RESULTS_DIR / "fig3_scatter_plots.png"
    plt.savefig(out, dpi=cfg["visualization"]["dpi"], bbox_inches="tight")
    plt.close()
    print(f"  [OK] {out.name}")


def fig4_moran_scatter(df: pd.DataFrame, cfg: dict):
    """Figure 4: Moran Scatter plot（bz_drug_rate）"""
    import libpysal
    from esda.moran import Moran

    gdf = load_merged_gdf(df)

    w = libpysal.weights.Queen.from_dataframe(gdf)
    if w.islands:
        w_knn = libpysal.weights.KNN.from_dataframe(gdf, k=2)
        for island in w.islands:
            for neighbor in w_knn.neighbors[island]:
                w.neighbors[island].append(neighbor)
                w.neighbors[neighbor].append(island)
        w = libpysal.weights.W(w.neighbors, silence_warnings=True)
    w.transform = "r"

    y   = gdf["bz_drug_rate"].values.astype(float)
    yz  = (y - y.mean()) / y.std()
    lag_yz = libpysal.weights.lag_spatial(w, yz)
    mi  = Moran(y, w, permutations=cfg["analysis"]["spatial"]["permutations"])

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(yz, lag_yz, c="#2c7fb8", alpha=0.7, s=50,
               edgecolors="white", linewidths=0.4)
    m, b = np.polyfit(yz, lag_yz, 1)
    xline = np.linspace(yz.min(), yz.max(), 100)
    ax.plot(xline, m * xline + b, "r-", linewidth=1.5)
    ax.axhline(0, color="grey", linewidth=0.6, linestyle="--")
    ax.axvline(0, color="grey", linewidth=0.6, linestyle="--")
    ax.set_xlabel("Standardized BZ Prescription Rate", fontsize=11)
    ax.set_ylabel("Spatial Lag (Mean of Neighbouring Prefectures)", fontsize=11)
    ax.set_title(f"Figure 4. Moran Scatter Plot\n"
                 f"I = {mi.I:.4f},  p = {mi.p_sim:.4f}",
                 fontsize=12)
    plt.tight_layout()
    out = RESULTS_DIR / "fig4_moran_scatter.png"
    plt.savefig(out, dpi=cfg["visualization"]["dpi"])
    plt.close()
    print(f"  [OK] {out.name}")


def main():
    print("=" * 60)
    print(" 07_visualization.py  可視化")
    print("=" * 60)

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from ndb_library.viz import set_japanese_font
    set_japanese_font()

    cfg  = load_config()
    df   = pd.read_csv(DATA_FILE,  encoding="utf-8-sig", dtype={"prefecture_code": str})
    sens = pd.read_csv(SENS_FILE,  encoding="utf-8-sig")

    print("\n[Figure 1] Choropleth map 作成中...")
    if not GEO_FILE.exists():
        print(f"  [SKIP] GeoJSONが見つかりません: {GEO_FILE}")
    else:
        gdf = load_merged_gdf(df)
        fig1_choropleth(df, gdf, cfg)

    print("[Figure 2] Forest plot 作成中...")
    fig2_forest_plot(sens, cfg)

    print("[Figure 3] Scatter plots 作成中...")
    fig3_scatter(df, cfg)

    print("[Figure 4] Moran scatter plot 作成中...")
    if not GEO_FILE.exists():
        print(f"  [SKIP] GeoJSONが見つかりません: {GEO_FILE}")
    else:
        fig4_moran_scatter(df, cfg)

    print(f"\n全図を {RESULTS_DIR} に保存しました。")
    print("=" * 60)


if __name__ == "__main__":
    main()
