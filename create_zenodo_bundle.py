"""
create_zenodo_bundle.py
Generates NDB_XXX_social_isolation_bz_zenodo_v1.0.0.zip for Zenodo deposit.

Whitelist-based: only explicitly listed files are included.
Run from the project root:
    python create_zenodo_bundle.py
"""

import zipfile
import os
from pathlib import Path

VERSION = "v1.0.0"
OUTPUT_ZIP = f"NDB_XXX_social_isolation_bz_zenodo_{VERSION}.zip"

# Whitelist: paths relative to project root
WHITELIST = [
    # Documentation
    "README.md",
    "CITATION.cff",
    "REPRODUCE.md",
    "DATA_SOURCES.md",
    "LICENSE",
    "docs/ZENODO_DEPOSIT_MANIFEST.md",
    # Config
    "config/config.yaml",
    # Analysis scripts
    "03_Analysis/scripts/01_extract_bz_drugs.py",
    "03_Analysis/scripts/02_fetch_census_isolation.py",
    "03_Analysis/scripts/03_load_secondary_outcomes.py",
    "03_Analysis/scripts/04_integrate_dataset.py",
    "03_Analysis/scripts/05_ols_regression.py",
    "03_Analysis/scripts/06_spatial_autocorrelation.py",
    "03_Analysis/scripts/07_visualization.py",
    # Figures
    "03_Analysis/results/fig1_choropleth_bz_rate.png",
    "03_Analysis/results/fig2_forest_plot_isolation.png",
    "03_Analysis/results/fig3_scatter_plots.png",
    "03_Analysis/results/fig4_moran_scatter.png",
    "03_Analysis/results/lisa_cluster_map.png",
    # Aggregate data (N=47, no individual-level data)
    "data/release/social_isolation_bz_analysis_dataset.csv",
    "data/release/social_isolation_bz_descriptive_stats.csv",
    "data/release/social_isolation_bz_regression_main.csv",
    "data/release/social_isolation_bz_sensitivity_analysis.csv",
    "data/release/social_isolation_bz_secondary_outcomes.csv",
    "data/release/social_isolation_bz_moran_results.csv",
    "data/release/social_isolation_bz_lisa_results.csv",
    # Manuscript source
    "04_Manuscripts/09Manuscript_social_isolation_bz_AGG_submission.qmd",
    "04_Manuscripts/highlights_social_isolation_bz.qmd",
    "04_Manuscripts/references.bib",
    "04_Manuscripts/apa.csl",
]

ROOT = Path(__file__).parent


def main():
    included = []
    missing = []

    with zipfile.ZipFile(OUTPUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel_path in WHITELIST:
            abs_path = ROOT / rel_path
            if abs_path.exists():
                arcname = f"NDB_XXX_social_isolation_bz_{VERSION}/{rel_path}"
                zf.write(abs_path, arcname)
                included.append(rel_path)
            else:
                missing.append(rel_path)

    print(f"\n{'='*60}")
    print(f"Zenodo bundle: {OUTPUT_ZIP}")
    print(f"{'='*60}")
    print(f"Included: {len(included)} files")
    for f in included:
        print(f"  + {f}")

    if missing:
        print(f"\nMISSING ({len(missing)} files — not included):")
        for f in missing:
            print(f"  ! {f}")

    zip_size_mb = os.path.getsize(OUTPUT_ZIP) / 1024 / 1024
    print(f"\nBundle size: {zip_size_mb:.1f} MB")
    print(f"\nNext steps:")
    print(f"  1. Review the bundle: python -c \"import zipfile; [print(f.filename) for f in zipfile.ZipFile('{OUTPUT_ZIP}').infolist()]\"")
    print(f"  2. Upload to Zenodo: https://zenodo.org/deposit/new")
    print(f"  3. Update DOI in CITATION.cff and 09Manuscript_*.qmd after deposit")


if __name__ == "__main__":
    main()
