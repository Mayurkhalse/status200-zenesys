"""
Confidence-Based Decision Policy.
Maps calibrated prediction confidence to routing decisions.
"""
import yaml

def evaluate_decision_policy(confidence: float, train_config_path: str = "config/training_config.yaml") -> str:
    """
    confidence >= HIGH_THRESHOLD    -> AUTO_ACCEPT
    MEDIUM_THRESHOLD <= conf < HIGH -> REVIEW / LLM_FALLBACK
    confidence < MEDIUM_THRESHOLD  -> UNKNOWN / HUMAN_REVIEW
    """
    try:
        with open(train_config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        thresholds = cfg.get("confidence_thresholds", {"high": 0.85, "medium": 0.60})
    except Exception:
        thresholds = {"high": 0.85, "medium": 0.60}

    high_t = thresholds.get("high", 0.85)
    med_t = thresholds.get("medium", 0.60)

    if confidence >= high_t:
        return "AUTO_ACCEPT"
    elif confidence >= med_t:
        return "REVIEW / LLM_FALLBACK"
    else:
        return "UNKNOWN / HUMAN_REVIEW"
