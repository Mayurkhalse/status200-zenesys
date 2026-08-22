"""
Semantic Sentence Embeddings Feature Extractor.
Uses sentence-transformers BGE/E5 models with fallback mode.
"""
import numpy as np

class SentenceEmbeddingExtractor:
    def __init__(self, config: dict):
        cfg = config.get("embeddings", {})
        self.model_id = cfg.get("model_id", "BAAI/bge-small-en-v1.5")
        self.dimension = cfg.get("dimension", 384)
        self.model = None

    def _load_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_id)
            except Exception as e:
                self.model = "fallback"

    def encode(self, texts: list) -> np.ndarray:
        self._load_model()
        if self.model != "fallback":
            try:
                return self.model.encode(texts, show_progress_bar=False)
            except Exception:
                pass
        
        # Fallback hash-vector embeddings
        embeddings = []
        for text in texts:
            vec = np.zeros(self.dimension)
            words = text.lower().split()
            for w in words:
                idx = hash(w) % self.dimension
                vec[idx] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm
            embeddings.append(vec)
        return np.array(embeddings)
