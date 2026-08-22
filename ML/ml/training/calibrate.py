"""
Probability Calibration Script.
Fits isotonic regression / Platt scaling calibrator per model using the validation split.
"""
import os, yaml, joblib
import numpy as np, pandas as pd
from scipy.sparse import load_npz, hstack
from sklearn.preprocessing import LabelEncoder
from ml.training.ensemble_model import SoftVotingEnsemble
from ml.training.calibrator_model import MultiClassCalibrator

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

    ensemble = joblib.load(paths["models"]["ensemble_pkl"])
    
    tfidf_mat = load_npz(paths["features"]["tfidf_matrix"])
    embeddings = np.load(paths["features"]["embeddings_npy"])
    X_sparse = hstack([tfidf_mat, embeddings]).tocsr()[val_indices]

    domain = pd.read_parquet(paths["features"]["domain_parquet"]).values
    stats = pd.read_parquet(paths["features"]["doc_stats_parquet"]).values
    layout = pd.read_parquet(paths["features"]["layout_parquet"]).values
    X_full = np.hstack([tfidf_mat.toarray(), embeddings, domain, stats, layout])[val_indices]

    X_dict = {}
    for name in ensemble.models_dict:
        if name in ["logistic_regression", "linear_svm"]:
            X_dict[name] = X_sparse
        else:
            X_dict[name] = X_full

    raw_probs = ensemble.predict_proba(X_dict)
    
    cal_method = train_config.get("calibration", {}).get("method", "isotonic")
    print(f"Fitting {cal_method} probability calibrator...")
    calibrator = MultiClassCalibrator(method=cal_method)
    calibrator.fit(raw_probs, y_val)

    joblib.dump(calibrator, paths["models"]["calibration_pkl"])
    print(f"Saved calibrator to: {paths['models']['calibration_pkl']}")

if __name__ == "__main__":
    main()
