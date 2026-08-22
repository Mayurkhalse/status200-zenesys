"""
TF-IDF Feature Extraction Module.
"""
from sklearn.feature_extraction.text import TfidfVectorizer

def build_tfidf_vectorizer(config: dict) -> TfidfVectorizer:
    """Instantiates a TfidfVectorizer based on feature config settings."""
    cfg = config.get("tfidf", {})
    ngram_range = tuple(cfg.get("ngram_range", [1, 2]))
    max_features = cfg.get("max_features", 10000)
    sublinear_tf = cfg.get("sublinear_tf", True)
    lowercase = cfg.get("lowercase", True)

    return TfidfVectorizer(
        ngram_range=ngram_range,
        max_features=max_features,
        sublinear_tf=sublinear_tf,
        lowercase=lowercase
    )
