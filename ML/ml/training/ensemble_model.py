"""
Soft Voting Ensemble Model Class.
Standalone module to ensure canonical pickle import path.
"""
import numpy as np

class SoftVotingEnsemble:
    def __init__(self, models_dict: dict, weights: dict = None):
        self.models_dict = models_dict
        self.weights = weights or {name: 1.0 for name in models_dict}

    def predict_proba(self, X_dict: dict) -> np.ndarray:
        total_weight = 0.0
        weighted_probs = None
        
        for name, model in self.models_dict.items():
            X = X_dict[name]
            if not hasattr(model, "multi_class"):
                setattr(model, "multi_class", "auto")
            probs = model.predict_proba(X)
            w = self.weights.get(name, 1.0)
            
            if weighted_probs is None:
                weighted_probs = probs * w
            else:
                weighted_probs += probs * w
            total_weight += w

        return weighted_probs / total_weight

    def predict(self, X_dict: dict) -> np.ndarray:
        probs = self.predict_proba(X_dict)
        return np.argmax(probs, axis=1)
