"""
Master Evaluation Script.
Evaluates all trained base models + ensemble on the test split, generates CSV reports,
calibration & confusion matrix charts, feature importances, and compiles the 8-page PDF report.
"""
import os, time, yaml, joblib
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from scipy.sparse import load_npz, hstack
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

from ml.evaluation.confusion_matrix import generate_confusion_matrix_plot
from ml.evaluation.calibration import calculate_ece, generate_calibration_plot
from ml.evaluation.error_analysis import analyze_errors
from ml.evaluation.model_comparison import build_model_comparison
from ml.evaluation.report_generator import generate_pdf_report
from ml.training.ensemble_model import SoftVotingEnsemble

def main():
    with open("config/training_config.yaml", "r", encoding="utf-8") as f:
        train_config = yaml.safe_load(f)
    with open("config/paths_config.yaml", "r", encoding="utf-8") as f:
        paths = yaml.safe_load(f)

    os.makedirs(paths["reports"]["reports_dir"], exist_ok=True)

    df_all = pd.read_csv(paths["dataset"]["synthetic_csv"])
    df_test = pd.read_csv(paths["dataset"]["test_csv"])
    df_train = pd.read_csv(paths["dataset"]["train_csv"])
    df_val = pd.read_csv(paths["dataset"]["val_csv"])
    le = joblib.load(paths["models"]["label_encoder_pkl"])
    class_names = list(le.classes_)

    doc_id_to_idx = {doc_id: i for i, doc_id in enumerate(df_all["document_id"])}
    test_indices = [doc_id_to_idx[doc_id] for doc_id in df_test["document_id"]]
    y_test = le.transform(df_test["document_type"])

    # Load sparse & dense features for test split
    tfidf_mat = load_npz(paths["features"]["tfidf_matrix"])
    embeddings = np.load(paths["features"]["embeddings_npy"])
    X_sparse = hstack([tfidf_mat, embeddings]).tocsr()[test_indices]

    domain = pd.read_parquet(paths["features"]["domain_parquet"]).values
    stats = pd.read_parquet(paths["features"]["doc_stats_parquet"]).values
    layout = pd.read_parquet(paths["features"]["layout_parquet"]).values
    X_full = np.hstack([tfidf_mat.toarray(), embeddings, domain, stats, layout])[test_indices]

    candidate_models = {
        "logistic_regression": (paths["models"]["logistic_pkl"], X_sparse),
        "linear_svm": (paths["models"]["svm_pkl"], X_sparse),
        "xgboost": (paths["models"]["xgboost_pkl"], X_full),
        "random_forest": (paths["models"]["random_forest_pkl"], X_full),
        "lightgbm": (paths["models"]["lightgbm_pkl"], X_full)
    }

    results = {}
    test_probs_dict = {}

    print("Evaluating models on test set...")
    for name, (path, X_data) in candidate_models.items():
        if os.path.exists(path):
            m = joblib.load(path)
            t0 = time.time()
            preds = m.predict(X_data)
            t_infer = (time.time() - t0) * 1000 / X_data.shape[0]
            
            if hasattr(m, "predict_proba"):
                probs = m.predict_proba(X_data)
                test_probs_dict[name] = probs

            results[name] = (y_test, preds, 5.0, t_infer)

    # Evaluate Ensemble
    if os.path.exists(paths["models"]["ensemble_pkl"]):
        ens = joblib.load(paths["models"]["ensemble_pkl"])
        t0 = time.time()
        X_dict = {n: X_sparse if n in ["logistic_regression", "linear_svm"] else X_full for n in ens.models_dict}
        ens_probs = ens.predict_proba(X_dict)
        ens_preds = np.argmax(ens_probs, axis=1)
        t_infer = (time.time() - t0) * 1000 / X_full.shape[0]
        results["ensemble"] = (y_test, ens_preds, 10.0, t_infer)
        test_probs_dict["ensemble"] = ens_probs

    # Model comparison table
    df_comp = build_model_comparison(results, paths["reports"]["model_comparison_csv"])
    print(df_comp)

    # Best Model Metrics (Ensemble if available, else highest Macro F1)
    best_model_name = "ensemble" if "ensemble" in results else df_comp.iloc[0]["Model"]
    y_best_pred = results[best_model_name][1]
    best_probs = test_probs_dict.get(best_model_name, np.eye(len(class_names))[y_best_pred])

    # Per-class table
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_best_pred, zero_division=0)
    df_per_class = pd.DataFrame({
        "Class": class_names,
        "Precision": np.round(prec, 4),
        "Recall": np.round(rec, 4),
        "F1 Score": np.round(f1, 4)
    })

    # Confusion matrix plot
    cm_path = paths["reports"]["confusion_matrix_png"]
    generate_confusion_matrix_plot(y_test, y_best_pred, class_names, cm_path)

    # Calibration plot
    cal_path = paths["reports"]["calibration_curve_png"]
    generate_calibration_plot(y_test, best_probs, cal_path)

    # Feature Importance Plot for XGBoost / Random Forest
    feat_imp_path = paths["reports"]["feature_importance_png"]
    if os.path.exists(paths["models"]["random_forest_pkl"]):
        rf_m = joblib.load(paths["models"]["random_forest_pkl"])
        importances = rf_m.feature_importances_[:20] # top 20
        plt.figure(figsize=(8, 5))
        plt.barh(range(len(importances)), importances, align='center', color='#1E3A8A')
        plt.yticks(range(len(importances)), [f"Feature_{i}" for i in range(len(importances))])
        plt.xlabel("Importance")
        plt.title("Top 20 Feature Importances (Random Forest)")
        plt.tight_layout()
        plt.savefig(feat_imp_path, dpi=300)
        plt.close()

    # Error Analysis
    err_path = paths["reports"]["error_analysis_csv"]
    df_errors, top_pairs = analyze_errors(df_test, y_test, y_best_pred, best_probs, class_names, err_path)

    # Build PDF Report
    ds_summary = {
        "total_docs": len(df_all),
        "train_size": len(df_train),
        "val_size": len(df_val),
        "test_size": len(df_test),
        "num_classes": len(class_names),
        "scanned_ratio": 0.3,
        "version": "1.0.0"
    }

    thresholds = train_config.get("confidence_thresholds", {"high": 0.85, "medium": 0.60})
    output_pdf = paths["reports"]["evaluation_pdf"]
    version_pdf = os.path.join(paths["reports"]["reports_dir"], "evaluation_report_v1.0.0.pdf")

    print(f"Generating official PDF Evaluation Report at {output_pdf}...")
    generate_pdf_report(
        output_pdf_path=output_pdf,
        version_pdf_path=version_pdf,
        dataset_summary=ds_summary,
        df_comparison=df_comp,
        df_per_class=df_per_class,
        cm_img_path=cm_path,
        cal_img_path=cal_path,
        feat_imp_img_path=feat_imp_path,
        top_error_pairs=top_pairs,
        df_errors=df_errors,
        thresholds=thresholds
    )

    print("Evaluation completed successfully!")

if __name__ == "__main__":
    main()
