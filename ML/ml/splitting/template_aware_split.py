"""
Template-Aware and Stratified Dataset Splitting.
Ensures zero template and company leakage across train, validation, and test splits.
"""
import os
import argparse
import yaml
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

def main():
    parser = argparse.ArgumentParser(description="Template-aware dataset split.")
    parser.add_argument("--paths", default="config/paths_config.yaml", help="Paths config")
    args = parser.parse_args()

    with open(args.paths, 'r', encoding='utf-8') as f:
        paths = yaml.safe_load(f)["dataset"]

    csv_path = paths["synthetic_csv"]
    splits_dir = paths["splits_dir"]
    os.makedirs(splits_dir, exist_ok=True)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Synthetic dataset CSV not found at {csv_path}. Run dataset generation first.")

    df = pd.read_csv(csv_path)

    # Group key for preventing template/company leakage
    df['group_key'] = df['document_type'].astype(str) + "_" + df['template_id'].astype(str) + "_" + df['company_name'].astype(str)

    # Split into 70% train and 30% temp (val + test)
    gss_train = GroupShuffleSplit(n_splits=1, train_size=0.70, random_state=42)
    train_idx, temp_idx = next(gss_train.split(df, groups=df['group_key']))

    train_df = df.iloc[train_idx]
    temp_df = df.iloc[temp_idx]

    # Split temp into 50% validation and 50% test (each 15% of total)
    gss_val = GroupShuffleSplit(n_splits=1, train_size=0.50, random_state=42)
    val_idx, test_idx = next(gss_val.split(temp_df, groups=temp_df['group_key']))

    val_df = temp_df.iloc[val_idx]
    test_df = temp_df.iloc[test_idx]

    # Save id lists
    train_df[['document_id', 'document_type', 'template_id', 'company_name']].to_csv(paths["train_csv"], index=False)
    val_df[['document_id', 'document_type', 'template_id', 'company_name']].to_csv(paths["val_csv"], index=False)
    test_df[['document_id', 'document_type', 'template_id', 'company_name']].to_csv(paths["test_csv"], index=False)

    print(f"Dataset Split Completed:")
    print(f"  Train samples: {len(train_df)} ({len(train_df)/len(df):.1%})")
    print(f"  Val samples:   {len(val_df)} ({len(val_df)/len(df):.1%})")
    print(f"  Test samples:  {len(test_df)} ({len(test_df)/len(df):.1%})")

if __name__ == "__main__":
    main()
