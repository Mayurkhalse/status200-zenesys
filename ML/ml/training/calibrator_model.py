"""
Multi-Class Calibrator Class.
Standalone module to ensure canonical pickle import path.
"""
import numpy as np
from sklearn.isotonic import IsotonicRegression

class MultiClassCalibrator:
    def __init__(self, method: str = "isotonic"):
        self.method = method
        self.calibrators = {}

    def fit(self, probs: np.ndarray, y_true: np.ndarray):
        n_classes = probs.shape[1]
        for c in range(n_classes):
            binary_y = (y_true == c).astype(int)
            cal = IsotonicRegression(out_of_bounds="clip")
            cal.fit(probs[:, c], binary_y)
            self.calibrators[c] = cal

    def calibrate(self, probs: np.ndarray) -> np.ndarray:
        cal_probs = np.zeros_like(probs)
        n_classes = probs.shape[1]
        for c in range(n_classes):
            if c in self.calibrators:
                cal_probs[:, c] = self.calibrators[c].transform(probs[:, c])
            else:
                cal_probs[:, c] = probs[:, c]
        row_sums = cal_probs.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        return cal_probs / row_sums
