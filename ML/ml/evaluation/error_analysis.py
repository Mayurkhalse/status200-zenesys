"""
Error Analysis Module.
Logs misclassifications to error_analysis.csv and computes top confusion pairs.
"""
import pandas as pd

def analyze_errors(df_test: pd.DataFrame, y_true: list, y_pred: list, probs: list, labels: list, output_csv: str):
    """Logs misclassified documents with predicted confidence and top confusion pairs."""
    records = []
    confusion_counts = {}

    for i in range(len(y_true)):
        t_label = labels[y_true[i]]
        p_label = labels[y_pred[i]]
        conf = float(probs[i][y_pred[i]])
        doc_id = df_test.iloc[i]["document_id"]

        if t_label != p_label:
            records.append({
                "document_id": doc_id,
                "actual": t_label,
                "predicted": p_label,
                "confidence": conf
            })
            pair = f"{t_label} -> {p_label}"
            confusion_counts[pair] = confusion_counts.get(pair, 0) + 1

    df_errors = pd.DataFrame(records)
    df_errors.to_csv(output_csv, index=False)
    
    # Sort top confusion pairs
    top_pairs = sorted(confusion_counts.items(), key=lambda x: x[1], reverse=True)
    return df_errors, top_pairs
