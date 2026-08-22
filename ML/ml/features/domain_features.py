"""
Domain-Specific Keyword Features Extractor.
Generates keyword hit vectors per document class.
"""
import numpy as np

class DomainFeatureExtractor:
    def __init__(self, config: dict):
        self.domain_keywords = config.get("domain_keywords", {})
        self.keyword_list = []
        for cls_name, keywords in self.domain_keywords.items():
            for kw in keywords:
                self.keyword_list.append(kw.lower())

    def extract_features(self, text: str) -> np.ndarray:
        text_lower = text.lower()
        vector = []
        for kw in self.keyword_list:
            count = text_lower.count(kw)
            vector.append(float(count))
        return np.array(vector)

    def extract_batch(self, texts: list) -> np.ndarray:
        return np.array([self.extract_features(t) for t in texts])
