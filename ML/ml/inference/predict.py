"""
Inference Module.
predict(model_artifacts, document_file_path) pipeline.
"""
import argparse, json, yaml
import numpy as np, pandas as pd
from scipy.sparse import hstack, csr_matrix

from ml.preprocessing.preprocess import process_document
from ml.features.embedding_features import SentenceEmbeddingExtractor
from ml.features.domain_features import DomainFeatureExtractor
from ml.features.document_statistics import extract_document_stats
from ml.features.layout_features import extract_layout_vector
from ml.inference.model_loader import load_trained_artifacts
from ml.inference.decision_policy import evaluate_decision_policy
from ml.training.ensemble_model import SoftVotingEnsemble
from ml.training.calibrator_model import MultiClassCalibrator

def predict_document(file_path: str, artifacts: dict = None) -> dict:
    """End-to-end single document inference."""
    if artifacts is None:
        artifacts = load_trained_artifacts()

    model = artifacts["model"]
    le = artifacts["label_encoder"]
    vectorizer = artifacts["vectorizer"]
    calibrator = artifacts["calibrator"]

    with open("config/feature_config.yaml", "r", encoding="utf-8") as f:
        feat_config = yaml.safe_load(f)

    # 1. Unified Preprocessing
    pdoc = process_document(file_path)
    text = pdoc.normalized_text

    # 2. Extract Features
    tfidf_vec = vectorizer.transform([text]) if vectorizer else csr_matrix((1, 10000))
    embedder = SentenceEmbeddingExtractor(feat_config)
    emb_vec = embedder.encode([text])
    
    domain_ext = DomainFeatureExtractor(feat_config)
    dom_vec = domain_ext.extract_batch([text])

    stat_vec = extract_document_stats(pdoc).reshape(1, -1)
    lay_vec = extract_layout_vector(pdoc).reshape(1, -1)

    X_sparse = hstack([tfidf_vec, emb_vec]).tocsr()
    X_full = np.hstack([tfidf_vec.toarray(), emb_vec, dom_vec, stat_vec, lay_vec])

    # Handle model prediction
    if hasattr(model, "predict_proba"):
        if hasattr(model, "models_dict"):
            X_dict = {n: X_sparse if n in ["logistic_regression", "linear_svm"] else X_full for n in model.models_dict}
            probs = model.predict_proba(X_dict)
        else:
            try:
                probs = model.predict_proba(X_full)
            except Exception:
                probs = model.predict_proba(X_sparse)
    else:
        probs = np.zeros((1, len(le.classes_)))

    if calibrator:
        probs = calibrator.calibrate(probs)

    probs = probs[0]
    top_indices = np.argsort(probs)[::-1]
    predicted_idx = top_indices[0]
    
    predicted_type = le.inverse_transform([predicted_idx])[0]
    confidence = float(probs[predicted_idx])
    
    prob_dict = {str(le.classes_[i]): float(probs[i]) for i in range(len(probs))}
    top_k = [str(le.classes_[i]) for i in top_indices[:3]]

    decision = evaluate_decision_policy(confidence)

    return {
        "document_type": predicted_type,
        "confidence": round(confidence, 4),
        "decision": decision,
        "top_k": top_k,
        "probabilities": prob_dict,
        "model_version": "1.0.0"
    }

def main():
    parser = argparse.ArgumentParser(description="Run document classifier inference.")
    parser.add_argument("--file", required=True, help="Path to input document")
    args = parser.parse_args()

    artifacts = load_trained_artifacts()
    res = predict_document(args.file, artifacts)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
