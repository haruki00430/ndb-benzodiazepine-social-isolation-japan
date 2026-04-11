import pandas as pd
import os
import sys

# Paths
PROJECT_ROOT = r"c:\Users\user\SharedWorkspace\projects\NDB_Research_Hub"
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "02_Data", "raw", "NDB_OpenData", "No.10")

def inspect_bz_drugs():
    target_files = []
    for root, dirs, files in os.walk(RAW_DATA_DIR):
        for file in files:
            if "05_" in root and file.endswith(".xlsx") and os.path.getsize(os.path.join(root, file)) > 1000000:
                target_files.append(os.path.join(root, file))

    print(f"Scanning {len(target_files)} files for Drug Codes 112 and 117...")
    
    found_drugs = {} # {code: name}
    
    for f in target_files:
        try:
            df = pd.read_excel(f, header=[2, 3])
            cols_flat = [" ".join([str(y) for y in x]) for x in df.columns]
            df.columns = cols_flat
            
            code_col = next((c for c in df.columns if "薬効" in c and "コード" in c), None)
            name_col = next((c for c in df.columns if "薬効" in c and "名称" in c), None)
            
            if not code_col or not name_col:
                continue
            
            df[code_col] = df[code_col].astype(str)
            target_df = df[df[code_col].str.startswith(('112', '117'))][[code_col, name_col]].drop_duplicates()
            
            for _, row in target_df.iterrows():
                code = row[code_col]
                name = row[name_col]
                if code not in found_drugs:
                    found_drugs[code] = name
            
            if len(found_drugs) > 50: break
                
        except Exception:
            pass

    print(f"\n--- Result: Found {len(found_drugs)} unique drug codes ---")
    
    print("\n[Code 112: Hypnotics/Sedatives Samples]")
    for c, n in sorted(found_drugs.items()):
        if c.startswith('112'):
            print(f"  {c}: {n}")

    print("\n[Code 117: Psychotropics Samples]")
    for c, n in sorted(found_drugs.items()):
        if c.startswith('117'):
            print(f"  {c}: {n}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    inspect_bz_drugs()
