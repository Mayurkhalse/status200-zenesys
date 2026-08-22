"""
Unit tests for Training & Soft Voting Ensemble.
"""
import numpy as np
from ml.training.train_ensemble import SoftVotingEnsemble

class DummyModel:
    def __init__(self, prob):
        self.prob = prob

    def predict_proba(self, X):
        return np.tile(self.prob, (len(X), 1))

def test_soft_voting_ensemble():
    m1 = DummyModel([0.8, 0.2])
    m2 = DummyModel([0.6, 0.4])
    ens = SoftVotingEnsemble({"m1": m1, "m2": m2}, weights={"m1": 1.0, "m2": 1.0})
    X_dict = {"m1": np.zeros((2, 5)), "m2": np.zeros((2, 5))}
    probs = ens.predict_proba(X_dict)
    assert probs.shape == (2, 2)
    assert np.isclose(probs[0][0], 0.7)
