"""
Ensemble Builder.
Inspects validation performance of trained base models, selects top N, and constructs a soft voting ensemble.
"""
import os, json, yaml, joblib
import numpy as np, pandas as pd
from scipy.sparse import load_npz, hstack
from sklearn.metrics import f1_score, accuracy_score
from ml.training.ensemble_model import SoftVotingEnsemble

def main():
    with open("config/training_config.yaml", "r", encoding="utf-8") as f:
        train_config = yaml.safe_load(f)
    with open("config/paths_config.yaml", "r", encoding="utf-8") as f:
        paths = yaml.safe_load(f)

    df_all = pd.read_csv(paths["dataset"]["synthetic_csv"])
    df_val = pd.read_csv(paths["dataset"]["val_csv"])
    le = joblib.load(paths["models"]["label_encoder_pkl"])

    doc_id_to_idx = {doc_id: i for i, doc_id in enumerate(df_all["document_id"])}
    val_indices = [doc_id_to_idx[doc_id] for doc_id in df_val["document_id"]]
    y_val = le.transform(df_val["document_type"])

    # Load sparse X for Linear models & dense X for Tree models
    tfidf_mat = load_npz(paths["features"]["tfidf_matrix"])
    embeddings = np.load(paths["features"]["embeddings_npy"])
    X_sparse = hstack([tfidf_mat, embeddings]).tocsr()[val_indices]

    domain = pd.read_parquet(paths["features"]["domain_parquet"]).values
    stats = pd.read_parquet(paths["features"]["doc_stats_parquet"]).values
    layout = pd.read_parquet(paths["features"]["layout_parquet"]).values
    X_full = np.hstack([tfidf_mat.toarray(), embeddings, domain, stats, layout])[val_indices]

    candidate_models = {
        "logistic_regression": (paths["models"]["logistic_pkl"], X_sparse),
        "linear_svm": (paths["models"]["svm_pkl"], X_sparse),
        "xgboost": (paths["models"]["xgboost_pkl"], X_full),
        "random_forest": (paths["models"]["random_forest_pkl"], X_full),
        "lightgbm": (paths["models"]["lightgbm_pkl"], X_full)
    }

    loaded_models = {}
    model_inputs = {}
    scores = {}

    print("Evaluating base models on validation split...")
    for name, (path, X_data) in candidate_models.items():
        if os.path.exists(path):
            m = joblib.load(path)
            preds = m.predict(X_data)
            score = f1_score(y_val, preds, average="macro")
            scores[name] = score
            loaded_models[name] = m
            model_inputs[name] = X_data
            print(f"  {name}: Macro-F1 = {score:.4f}")

    top_n = train_config.get("ensemble", {}).get("top_n", 3)
    sorted_models = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    selected_names = [name for name, _ in sorted_models]
    print(f"Selected top {len(selected_names)} base models for ensemble: {selected_names}")

    selected_dict = {name: loaded_models[name] for name in selected_names}
    weights = {name: scores[name] for name in selected_names}

    ensemble = SoftVotingEnsemble(selected_dict, weights)
    
    val_X_dict = {name: model_inputs[name] for name in selected_names}
    ens_preds = ensemble.predict(val_X_dict)
    ens_acc = accuracy_score(y_val, ens_preds)
    ens_f1 = f1_score(y_val, ens_preds, average="macro")

    print(f"Ensemble Validation Accuracy: {ens_acc:.4f}, Macro-F1: {ens_f1:.4f}")
    joblib.dump(ensemble, paths["models"]["ensemble_pkl"])
    print(f"Saved Ensemble to: {paths['models']['ensemble_pkl']}")

if __name__ == "__main__":
    main()
