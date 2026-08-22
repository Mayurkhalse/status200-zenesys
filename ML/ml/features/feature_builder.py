"""
Feature Builder Orchestrator.
Combines all 5 feature groups (TF-IDF, Embeddings, Domain Indicators, Doc Stats, Layout),
saves feature matrices under features/cache/, and generates feature_manifest.json.
"""
import os
import json
import yaml
import joblib
import numpy as np
import pandas as pd
from scipy.sparse import save_npz, load_npz, hstack

from ml.preprocessing.preprocess import process_document
from ml.features.tfidf_features import build_tfidf_vectorizer
from ml.features.embedding_features import SentenceEmbeddingExtractor
from ml.features.domain_features import DomainFeatureExtractor
from ml.features.document_statistics import extract_batch_stats
from ml.features.layout_features import extract_batch_layout

def main():
    with open("config/feature_config.yaml", "r", encoding="utf-8") as f:
        feat_config = yaml.safe_load(f)
    with open("config/paths_config.yaml", "r", encoding="utf-8") as f:
        paths = yaml.safe_load(f)

    cache_dir = paths["features"]["cache_dir"]
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(paths["models"]["classifier_dir"], exist_ok=True)

    csv_path = paths["dataset"]["synthetic_csv"]
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Synthetic data not found at {csv_path}. Run document generation first.")

    df = pd.read_csv(csv_path)
    print(f"Building features for {len(df)} documents...")

    parsed_docs = []
    texts = []
    for idx, row in df.iterrows():
        # Resolve paths relative to dataset folder
        abs_pdf = os.path.join("dataset", row["file_path_pdf"])
        abs_png = os.path.join("dataset", row["file_path_png"])
        
        target_path = abs_pdf if os.path.exists(abs_pdf) else abs_png

        pdoc = process_document(target_path)
        parsed_docs.append(pdoc)
        texts.append(pdoc.normalized_text)

    # 1. TF-IDF Features
    print("Extracting TF-IDF features...")
    vectorizer = build_tfidf_vectorizer(feat_config)
    tfidf_matrix = vectorizer.fit_transform(texts)
    save_npz(paths["features"]["tfidf_matrix"], tfidf_matrix)
    joblib.dump(vectorizer, paths["models"]["tfidf_vectorizer_pkl"])

    # 2. Semantic Embeddings
    print("Extracting Semantic Embeddings...")
    embedder = SentenceEmbeddingExtractor(feat_config)
    embeddings = embedder.encode(texts)
    np.save(paths["features"]["embeddings_npy"], embeddings)
    with open(paths["models"]["embedding_model_ref"], "w", encoding="utf-8") as f:
        json.dump({"model_id": embedder.model_id, "dimension": embedder.dimension}, f, indent=2)

    # 3. Domain Keyword Indicators
    print("Extracting Domain Keyword Indicators...")
    domain_ext = DomainFeatureExtractor(feat_config)
    domain_feats = domain_ext.extract_batch(texts)
    pd.DataFrame(domain_feats).to_parquet(paths["features"]["domain_parquet"])

    # 4. Document Statistics
    print("Extracting Document Statistics...")
    stats_feats = extract_batch_stats(parsed_docs)
    pd.DataFrame(stats_feats).to_parquet(paths["features"]["doc_stats_parquet"])

    # 5. Layout Features
    print("Extracting Layout Features...")
    layout_feats = extract_batch_layout(parsed_docs)
    pd.DataFrame(layout_feats).to_parquet(paths["features"]["layout_parquet"])

    # Manifest creation
    manifest = {
        "num_documents": len(df),
        "feature_groups": {
            "tfidf": {"shape": list(tfidf_matrix.shape), "file": paths["features"]["tfidf_matrix"]},
            "embeddings": {"shape": list(embeddings.shape), "file": paths["features"]["embeddings_npy"]},
            "domain_indicators": {"shape": list(domain_feats.shape), "file": paths["features"]["domain_parquet"]},
            "document_statistics": {"shape": list(stats_feats.shape), "file": paths["features"]["doc_stats_parquet"]},
            "layout": {"shape": list(layout_feats.shape), "file": paths["features"]["layout_parquet"]}
        },
        "created_at": pd.Timestamp.now().isoformat()
    }

    with open(paths["features"]["manifest"], "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Feature building completed! Manifest written to: {paths['features']['manifest']}")

if __name__ == "__main__":
    main()
