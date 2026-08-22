"""
Train Logistic Regression Classifier.
Uses TF-IDF + Embeddings features.
"""
import os, json, yaml, joblib
import numpy as np, pandas as pd
from scipy.sparse import load_npz, hstack
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, accuracy_score, f1_score

def main():
    with open("config/training_config.yaml", "r", encoding="utf-8") as f:
        train_config = yaml.safe_load(f)
    with open("config/paths_config.yaml", "r", encoding="utf-8") as f:
        paths = yaml.safe_load(f)

    df_all = pd.read_csv(paths["dataset"]["synthetic_csv"])
    df_train = pd.read_csv(paths["dataset"]["train_csv"])
    df_val = pd.read_csv(paths["dataset"]["val_csv"])

    # Load Label Encoder
    le_path = paths["models"]["label_encoder_pkl"]
    if os.path.exists(le_path):
        le = joblib.load(le_path)
    else:
        le = LabelEncoder()
        le.fit(df_all["document_type"])
        joblib.dump(le, le_path)

    # Map indices
    doc_id_to_idx = {doc_id: i for i, doc_id in enumerate(df_all["document_id"])}
    train_indices = [doc_id_to_idx[doc_id] for doc_id in df_train["document_id"]]
    val_indices = [doc_id_to_idx[doc_id] for doc_id in df_val["document_id"]]

    y_train = le.transform(df_train["document_type"])
    y_val = le.transform(df_val["document_type"])

    # Load TF-IDF & Embeddings
    tfidf_mat = load_npz(paths["features"]["tfidf_matrix"])
    embeddings = np.load(paths["features"]["embeddings_npy"])

    X_sparse = hstack([tfidf_mat, embeddings])
    X_train = X_sparse.tocsr()[train_indices]
    X_val = X_sparse.tocsr()[val_indices]

    params = train_config["hyperparameters"]["logistic_regression"]
    print(f"Training Logistic Regression with params: {params}...")
    model = LogisticRegression(**params)
    model.fit(X_train, y_train)
    model.multi_class = "auto"

    val_preds = model.predict(X_val)
    acc = accuracy_score(y_val, val_preds)
    macro_f1 = f1_score(y_val, val_preds, average="macro")

    print(f"Logistic Regression Validation Accuracy: {acc:.4f}, Macro-F1: {macro_f1:.4f}")
    joblib.dump(model, paths["models"]["logistic_pkl"])
    print(f"Saved model to: {paths['models']['logistic_pkl']}")

if __name__ == "__main__":
    main()
