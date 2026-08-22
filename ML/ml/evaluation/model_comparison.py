"""
Model Comparison Table Builder.
"""
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def build_model_comparison(results_dict: dict, output_csv: str) -> pd.DataFrame:
    """
    results_dict format: { model_name: (y_true, y_pred, train_time, infer_time) }
    """
    rows = []
    for name, (y_true, y_pred, train_t, infer_t) in results_dict.items():
        acc = accuracy_score(y_true, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
        w_prec, w_rec, w_f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)

        rows.append({
            "Model": name,
            "Accuracy": round(acc, 4),
            "Macro Precision": round(prec, 4),
            "Macro Recall": round(rec, 4),
            "Macro F1": round(f1, 4),
            "Weighted F1": round(w_f1, 4),
            "Train Time (s)": round(train_t, 2),
            "Inference Time (ms/doc)": round(infer_t, 2)
        })

    df_comp = pd.DataFrame(rows)
    df_comp.to_csv(output_csv, index=False)
    return df_comp
