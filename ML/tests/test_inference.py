"""
Unit tests for Decision Policy & Inference.
"""
from ml.inference.decision_policy import evaluate_decision_policy

def test_decision_policy():
    assert evaluate_decision_policy(0.95) == "AUTO_ACCEPT"
    assert evaluate_decision_policy(0.70) == "REVIEW / LLM_FALLBACK"
    assert evaluate_decision_policy(0.40) == "UNKNOWN / HUMAN_REVIEW"
