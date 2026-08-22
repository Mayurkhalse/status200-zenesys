"""
Calibration Metrics & Plotting.
Calculates Brier Score, Expected Calibration Error (ECE), and generates calibration curve.
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import brier_score_loss

def calculate_ece(y_true_onehot: np.ndarray, probs: np.ndarray, n_bins: int = 10) -> float:
    """Calculates Expected Calibration Error (ECE)."""
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    true_labels = np.argmax(y_true_onehot, axis=1)
    accuracies = (predictions == true_labels)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)
        
        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(accuracies[in_bin])
            avg_confidence_in_bin = np.mean(confidences[in_bin])
            ece += np.abs(accuracy_in_bin - avg_confidence_in_bin) * prop_in_bin

    return ece

def generate_calibration_plot(y_true, probs, output_path: str):
    """Plots multi-class calibration curves."""
    plt.figure(figsize=(8, 6))
    confidences = np.max(probs, axis=1)
    predictions = np.argmax(probs, axis=1)
    accuracies = (predictions == y_true)

    bins = np.linspace(0, 1, 10)
    bin_accs = []
    bin_confs = []

    for i in range(len(bins)-1):
        mask = (confidences >= bins[i]) & (confidences < bins[i+1])
        if np.sum(mask) > 0:
            bin_accs.append(np.mean(accuracies[mask]))
            bin_confs.append(np.mean(confidences[mask]))

    plt.plot([0, 1], [0, 1], 'k--', label='Perfectly Calibrated')
    plt.plot(bin_confs, bin_accs, 's-', color='#1E3A8A', label='Model Calibration')
    plt.xlabel('Mean Predicted Probability')
    plt.ylabel('Fraction of Positives (Accuracy)')
    plt.title('Reliability Diagram (Calibration Curve)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
