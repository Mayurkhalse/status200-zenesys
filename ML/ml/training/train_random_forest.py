"""
Train Random Forest Classifier.
Uses combined feature bundle.
"""
import os, json, yaml, joblib
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestClassifier
from scipy.sparse import load_npz
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score

def get_full_feature_matrix(paths):
    tfidf_mat = load_npz(paths["features"]["tfidf_matrix"]).toarray()
    embeddings = np.load(paths["features"]["embeddings_npy"])
    domain = pd.read_parquet(paths["features"]["domain_parquet"]).values
    stats = pd.read_parquet(paths["features"]["doc_stats_parquet"]).values
    layout = pd.read_parquet(paths["features"]["layout_parquet"]).values
    return np.hstack([tfidf_mat, embeddings, domain, stats, layout])

def main():
    with open("config/training_config.yaml", "r", encoding="utf-8") as f:
        train_config = yaml.safe_load(f)
    with open("config/paths_config.yaml", "r", encoding="utf-8") as f:
        paths = yaml.safe_load(f)

    df_all = pd.read_csv(paths["dataset"]["synthetic_csv"])
    df_train = pd.read_csv(paths["dataset"]["train_csv"])
    df_val = pd.read_csv(paths["dataset"]["val_csv"])

    le = joblib.load(paths["models"]["label_encoder_pkl"])
    doc_id_to_idx = {doc_id: i for i, doc_id in enumerate(df_all["document_id"])}
    train_indices = [doc_id_to_idx[doc_id] for doc_id in df_train["document_id"]]
    val_indices = [doc_id_to_idx[doc_id] for doc_id in df_val["document_id"]]

    y_train = le.transform(df_train["document_type"])
    y_val = le.transform(df_val["document_type"])

    X_full = get_full_feature_matrix(paths)
    X_train = X_full[train_indices]
    X_val = X_full[val_indices]

    params = train_config["hyperparameters"]["random_forest"]
    print(f"Training Random Forest with params: {params}...")
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    val_preds = model.predict(X_val)
    acc = accuracy_score(y_val, val_preds)
    macro_f1 = f1_score(y_val, val_preds, average="macro")

    print(f"Random Forest Validation Accuracy: {acc:.4f}, Macro-F1: {macro_f1:.4f}")
    joblib.dump(model, paths["models"]["random_forest_pkl"])
    print(f"Saved model to: {paths['models']['random_forest_pkl']}")

if __name__ == "__main__":
    main()
