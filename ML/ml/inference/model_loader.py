"""
Model Loader Utility.
Loads trained classifier artifacts (ensemble/models, tfidf vectorizer, label encoder, calibration).
"""
import os, json, joblib
import yaml
from ml.training.ensemble_model import SoftVotingEnsemble
from ml.training.calibrator_model import MultiClassCalibrator

def load_trained_artifacts(paths_config_path: str = "config/paths_config.yaml") -> dict:
    """Loads all model artifacts required for inference."""
    with open(paths_config_path, "r", encoding="utf-8") as f:
        paths = yaml.safe_load(f)

    models_dir = paths["models"]["classifier_dir"]
    
    le_path = paths["models"]["label_encoder_pkl"]
    if not os.path.exists(le_path):
        raise FileNotFoundError(f"Label encoder not found at {le_path}. Train the pipeline first.")
    label_encoder = joblib.load(le_path)

    vec_path = paths["models"]["tfidf_vectorizer_pkl"]
    vectorizer = joblib.load(vec_path) if os.path.exists(vec_path) else None

    ref_path = paths["models"]["embedding_model_ref"]
    embed_ref = json.load(open(ref_path)) if os.path.exists(ref_path) else {}

    ens_path = paths["models"]["ensemble_pkl"]
    if os.path.exists(ens_path):
        model = joblib.load(ens_path)
    elif os.path.exists(paths["models"]["xgboost_pkl"]):
        model = joblib.load(paths["models"]["xgboost_pkl"])
    else:
        model = joblib.load(paths["models"]["logistic_pkl"])

    cal_path = paths["models"]["calibration_pkl"]
    calibrator = joblib.load(cal_path) if os.path.exists(cal_path) else None

    return {
        "model": model,
        "label_encoder": label_encoder,
        "vectorizer": vectorizer,
        "embedding_ref": embed_ref,
        "calibrator": calibrator,
        "paths": paths
    }
