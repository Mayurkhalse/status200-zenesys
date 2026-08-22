# ERP Document Classification — ML System

A modular, reproducible ML pipeline that generates synthetic ERP business documents, trains a document-type classifier (Task A), and lays the architecture groundwork for per-document specialized extraction models (Task B).

```
Synthetic Business Documents → Dataset Generation → Preprocessing → Feature Extraction
      → Model Training → Model Evaluation → Best Model Selection
      → Saved Model Files → Inference API
```

---

## 1. Document Classes

```
BUSINESS_INVOICE   PURCHASE_ORDER   SALES_ORDER   QUOTATION
PROPOSAL           CONTRACT         LEAD          RECEIPT
DELIVERY_NOTE      CREDIT_NOTE      DEBIT_NOTE    PAYMENT_RECEIPT
RFQ                OTHER
```

---

## 2. Repository / File Structure

```text
erp-doc-classifier/
│
├── config/
│   ├── generation_config.yaml          # documents_per_class, industries, currencies, formats
│   ├── feature_config.yaml             # tfidf params, embedding model id, domain keyword lists
│   ├── training_config.yaml            # model hyperparams, ensemble weights, thresholds
│   └── paths_config.yaml               # canonical paths used by every script
│
├── dataset/
│   ├── raw/
│   │   ├── BUSINESS_INVOICE/
│   │   │   ├── template_001/
│   │   │   │   ├── doc_000001.pdf
│   │   │   │   ├── doc_000001.docx
│   │   │   │   └── doc_000001.png
│   │   │   ├── template_002/
│   │   │   └── ...
│   │   ├── PURCHASE_ORDER/
│   │   ├── SALES_ORDER/
│   │   ├── QUOTATION/
│   │   ├── PROPOSAL/
│   │   ├── CONTRACT/
│   │   ├── LEAD/
│   │   ├── RECEIPT/
│   │   ├── DELIVERY_NOTE/
│   │   ├── CREDIT_NOTE/
│   │   ├── DEBIT_NOTE/
│   │   ├── PAYMENT_RECEIPT/
│   │   ├── RFQ/
│   │   └── OTHER/
│   │
│   ├── synthetic_data.csv              # ★ flat, tabular record of every generated document
│   ├── metadata.jsonl                  # same info, one JSON object per line (kept in sync with CSV)
│   ├── extraction_ground_truth/        # per-type field-level ground truth for future Task B models
│   │   ├── invoice_ground_truth.csv
│   │   ├── purchase_order_ground_truth.csv
│   │   ├── contract_ground_truth.csv
│   │   └── ...
│   └── splits/
│       ├── train.csv                   # document_id list, template-aware & stratified
│       ├── validation.csv
│       └── test.csv
│
├── features/
│   ├── cache/
│   │   ├── tfidf_matrix.npz
│   │   ├── embeddings.npy
│   │   ├── domain_indicator_features.parquet
│   │   ├── document_statistics.parquet
│   │   └── layout_features.parquet
│   └── feature_manifest.json           # which feature groups + versions went into each model
│
├── ml/
│   ├── dataset_generation/
│   │   ├── generate_documents.py       # orchestrator, reads generation_config.yaml
│   │   ├── generate_invoice.py
│   │   ├── generate_purchase_order.py
│   │   ├── generate_sales_order.py
│   │   ├── generate_quotation.py
│   │   ├── generate_proposal.py
│   │   ├── generate_contract.py
│   │   ├── generate_lead.py
│   │   ├── generate_receipt.py
│   │   ├── generate_delivery_note.py
│   │   ├── generate_credit_note.py
│   │   ├── generate_debit_note.py
│   │   ├── generate_payment_receipt.py
│   │   ├── generate_rfq.py
│   │   ├── generate_other.py
│   │   ├── entity_pools.py             # fake companies, cities, currencies, products per industry
│   │   ├── layout_renderer.py          # renders HTML/DOCX layout -> PDF/DOCX/PNG
│   │   ├── scan_simulator.py           # blur / noise / rotation / skew / brightness
│   │   └── csv_writer.py               # appends every generated doc's row to synthetic_data.csv
│   │
│   ├── splitting/
│   │   └── template_aware_split.py     # builds train/validation/test.csv, no template leakage
│   │
│   ├── preprocessing/
│   │   ├── preprocess.py               # orchestrator: validate -> extract -> normalize
│   │   ├── file_validation.py
│   │   ├── text_extraction_pdf.py      # PyMuPDF
│   │   ├── text_extraction_docx.py     # python-docx
│   │   ├── ocr.py                      # PaddleOCR for scanned-style docs
│   │   ├── text_normalization.py
│   │   └── extract_layout.py           # bounding boxes, blocks, header/footer detection
│   │
│   ├── features/
│   │   ├── tfidf_features.py
│   │   ├── embedding_features.py       # BGE / E5 sentence-transformers
│   │   ├── domain_features.py          # per-class keyword indicator vectors
│   │   ├── document_statistics.py
│   │   ├── layout_features.py          # stored for future LayoutLMv3 use
│   │   └── feature_builder.py          # combines all groups into one matrix per model type
│   │
│   ├── training/
│   │   ├── train_logistic.py
│   │   ├── train_svm.py
│   │   ├── train_xgboost.py
│   │   ├── train_random_forest.py
│   │   ├── train_lightgbm.py
│   │   ├── train_ensemble.py           # soft/weighted voting over strongest base models
│   │   └── calibrate.py                # Platt scaling / isotonic regression per model
│   │
│   ├── evaluation/
│   │   ├── evaluate.py                 # computes all metrics, orchestrates report generation
│   │   ├── confusion_matrix.py
│   │   ├── calibration.py              # calibration curve, Brier score, ECE
│   │   ├── error_analysis.py           # misclassification log + confusion-pair analysis
│   │   ├── model_comparison.py
│   │   └── report_generator.py         # ★ builds the final evaluation_report.pdf
│   │
│   └── inference/
│       ├── predict.py                  # load_model() / predict(document)
│       ├── model_loader.py
│       └── decision_policy.py          # HIGH/MEDIUM/LOW confidence routing
│
├── models/
│   ├── document_classifier/
│   │   ├── ensemble.pkl
│   │   ├── xgboost_model.pkl
│   │   ├── svm_model.pkl
│   │   ├── random_forest.pkl
│   │   ├── lightgbm_model.pkl
│   │   ├── logistic_regression.pkl
│   │   ├── tfidf_vectorizer.pkl
│   │   ├── embedding_model_ref.json    # model id/path for BGE or E5
│   │   ├── label_encoder.pkl
│   │   ├── scaler.pkl
│   │   ├── calibration.pkl
│   │   └── metadata.json
│   │
│   ├── invoice/                        # future specialized models (structured extraction for v1)
│   │   ├── invoice_config.json
│   │   └── invoice_model.pkl           # placeholder until NER/LayoutLM model is trained
│   ├── purchase_order/
│   ├── contract/
│   ├── proposal/
│   └── ...                             # one folder per class, created on demand
│
├── reports/
│   ├── evaluation_report.pdf           # ★ auto-generated after every training run
│   ├── evaluation_report_v1.0.0.pdf    # versioned copy, kept for comparison across runs
│   ├── confusion_matrix.png
│   ├── calibration_curve.png
│   ├── feature_importance.png
│   ├── model_comparison_table.csv
│   └── error_analysis.csv
│
├── api/
│   ├── inference_service.py            # FastAPI/Flask wrapper around ml/inference/predict.py
│   └── schemas.py                      # request/response pydantic models
│
├── tests/
│   ├── test_generation.py
│   ├── test_preprocessing.py
│   ├── test_features.py
│   ├── test_training.py
│   └── test_inference.py
│
├── requirements.txt
└── README.md
```

---

## 3. Low-Level Design

### 3.1 Dataset Generation

`generate_documents.py` reads `generation_config.yaml` (`documents_per_class`, industries, currencies, formats, scan-simulation probability) and, for each class, calls the matching `generate_<type>.py` module in a loop.

Each `generate_<type>.py`:
1. Picks a random template id for that class.
2. Pulls entities from `entity_pools.py` (company, customer/vendor, address, industry, currency, products).
3. Fills the template's content model (a plain Python dict of fields).
4. Passes the filled content to `layout_renderer.py`, which renders one of several HTML/DOCX layouts for that class into PDF, DOCX, and PNG.
5. Optionally routes the PNG/PDF through `scan_simulator.py` to produce a "scanned-style" degraded copy (blur, noise, rotation, skew, compression, brightness).
6. Emits one row of structured data, which `csv_writer.py` appends to `dataset/synthetic_data.csv`, and the same record is written as a line to `dataset/metadata.jsonl`.
7. If the class has an extraction ground-truth schema (invoice, PO, contract, ...), the field-level values used to fill the template are also written to `dataset/extraction_ground_truth/<type>_ground_truth.csv` — this is the training data for future Task B models.

**`dataset/synthetic_data.csv` schema (one row per generated document):**

| column | example |
|---|---|
| document_id | DOC_000123 |
| file_path_pdf | raw/BUSINESS_INVOICE/template_007/doc_000123.pdf |
| file_path_docx | raw/BUSINESS_INVOICE/template_007/doc_000123.docx |
| file_path_png | raw/BUSINESS_INVOICE/template_007/doc_000123.png |
| document_type | BUSINESS_INVOICE |
| template_id | invoice_template_07 |
| industry | IT_SERVICES |
| country | India |
| currency | INR |
| company_name | Nova Systems India |
| counterparty_name | ABC Technologies Pvt Ltd |
| is_scanned_style | False |
| degradation_type | none |
| generated_at | 2026-08-22T10:14:00Z |
| generator_version | 1.0.0 |

`dataset/metadata.jsonl` mirrors the same fields in JSON-per-line form for tooling that prefers JSON.

### 3.2 Template-Aware Splitting

`template_aware_split.py` groups documents by `(document_type, template_id)` and, where possible, by `company_name`, then assigns whole groups to train/validation/test so that no template or company appears in more than one split. Splits are stratified by class to keep the 70/15/15 ratio per class. Output is three id-list files under `dataset/splits/`, not copies of the documents themselves.

### 3.3 Preprocessing

`preprocess.py` is the single entry point used both at training time and at inference time (imported by `ml/inference/predict.py`), so preprocessing logic is never duplicated:

```
file validation → text extraction (PyMuPDF / python-docx) → OCR if scanned (PaddleOCR)
→ text normalization → layout extraction (blocks, bounding boxes, header/footer, columns)
```

Output is a normalized in-memory `ParsedDocument` object (text, tokens, layout blocks) consumed by every feature extractor.

### 3.4 Feature Extraction

`feature_builder.py` combines five feature groups into a single feature bundle per document:

- **TF-IDF** (`tfidf_features.py`) — `TfidfVectorizer(ngram_range=(1,2), max_features=10000, sublinear_tf=True)`, fit on train split only.
- **Semantic embeddings** (`embedding_features.py`) — pretrained BGE/E5 sentence-transformer, model id set in `feature_config.yaml`; embeddings cached to `features/cache/embeddings.npy`.
- **Domain indicators** (`domain_features.py`) — per-class keyword hit vectors (invoice: "invoice number", "GST", "amount due"...; contract: "jurisdiction", "termination"...; etc.), one binary/count vector per class's keyword list.
- **Document statistics** (`document_statistics.py`) — page count, word/line/table/image counts, text density, average word length.
- **Layout features** (`layout_features.py`) — bounding boxes, column count, header/footer presence, table positions; stored in full so a future LayoutLMv3 model can reuse them without re-parsing documents.

TF-IDF and embeddings feed the linear models; the full combined bundle feeds the tree-based models (XGBoost, Random Forest, LightGBM). `feature_manifest.json` records exactly which feature versions were used for each saved model, for reproducibility.

### 3.5 Training

Each `train_<model>.py` script loads the appropriate feature bundle for the train split, fits the model, evaluates on validation, and saves the raw model artifact to `models/document_classifier/`. `train_ensemble.py` runs last: it inspects validation Macro-F1 for every trained base model, selects the strongest subset (not necessarily all of them), and builds a soft/weighted voting ensemble. `calibrate.py` fits Platt scaling or isotonic regression per selected model using the validation split and saves `calibration.pkl`.

### 3.6 Evaluation & the PDF Metrics Report

`evaluate.py` is the orchestrator that runs after every training run:

1. Loads the test split, runs every trained model + the ensemble through `ml/inference/predict.py`.
2. Computes: accuracy, macro/weighted precision/recall/F1, per-class F1, confusion matrix (`confusion_matrix.py`), calibration curve / Brier score / Expected Calibration Error (`calibration.py`), training time, inference time, and feature importance (for tree models).
3. Runs `error_analysis.py`, which logs every misclassified document (`document_id`, `actual`, `predicted`, `confidence`) to `reports/error_analysis.csv` and aggregates the most common confusion pairs (e.g. `PROPOSAL ↔ QUOTATION`).
4. Passes all computed metrics, charts, and tables to **`report_generator.py`**, which assembles `reports/evaluation_report.pdf` using `matplotlib`/`seaborn` for charts and a PDF layout library (e.g. `reportlab` or `matplotlib.backends.backend_pdf.PdfPages`) to lay out the final document. This is triggered automatically at the end of the training pipeline — no manual step required.

**`evaluation_report.pdf` contents, in order:**

```
Page 1  — Dataset summary: class distribution, split sizes, generation config used
Page 2  — Model comparison table (Accuracy, Macro-F1, Weighted-F1, train/inference time)
Page 3  — Per-class precision/recall/F1 table, for the selected best model
Page 4  — Confusion matrix heatmap
Page 5  — Calibration curve + Brier score + Expected Calibration Error
Page 6  — Feature importance chart (tree-based models)
Page 7  — Error analysis: top confusion pairs, sample misclassified document IDs
Page 8  — Chosen confidence thresholds (HIGH / MEDIUM / LOW) and rationale
```

Every run also writes a version-stamped copy (`evaluation_report_<version>.pdf`) so historical runs can be diffed. The underlying numbers behind the PDF are also saved as `reports/model_comparison_table.csv` and `reports/error_analysis.csv` for programmatic use.

### 3.7 Confidence-Based Decision Policy

`decision_policy.py` reads thresholds chosen from validation performance (not hardcoded) and maps a calibrated confidence score to:

```
confidence ≥ HIGH_THRESHOLD    → AUTO_ACCEPT
MEDIUM_THRESHOLD ≤ conf < HIGH → REVIEW / LLM_FALLBACK
confidence < MEDIUM_THRESHOLD  → UNKNOWN / HUMAN_REVIEW
```

Thresholds are stored in `models/document_classifier/metadata.json` alongside the model version.

### 3.8 Inference

```python
from ml.inference.predict import load_model, predict

model = load_model(version="1.0.0")
result = predict(model, document)
```

```json
{
  "document_type": "BUSINESS_INVOICE",
  "confidence": 0.97,
  "probabilities": { "...": "..." },
  "top_k": ["BUSINESS_INVOICE", "RECEIPT", "QUOTATION"],
  "decision": "AUTO_ACCEPT",
  "model_version": "1.0.0"
}
```

`predict.py` calls the same `preprocess.py` and `feature_builder.py` used in training, loading every saved artifact (vectorizer, embedding model reference, encoder, scaler, calibration) from `models/document_classifier/` — nothing is recomputed or reimplemented at inference time.

### 3.9 Specialized (Task B) Architecture — Future-Ready, Not Built Yet

`models/<type>/` folders and `dataset/extraction_ground_truth/<type>_ground_truth.csv` files are created for every class from day one, even though v1 only does structured/rule-based extraction. This lets a future model reuse:

```
Document → type-specific preprocessing → OCR + layout → token embeddings
→ layout-aware model (e.g. LayoutLMv3) → NER / token classification
→ field extraction → structured JSON
```

Layout features saved during Task A preprocessing (`features/cache/layout_features.parquet`) already contain the token/bounding-box information LayoutLMv3-style models need, so switching a document type from rule-based extraction to a trained NER/LayoutLM model does not require re-parsing the original documents.

---

## 4. Configuration

All tunables live in `config/*.yaml`, most importantly:

```yaml
# generation_config.yaml
documents_per_class: 1000        # override to 100 / 250 / 500 for dev runs
formats: [pdf, docx, png]
scanned_style_ratio: 0.3
industries: [IT_SERVICES, MANUFACTURING, RETAIL, HEALTHCARE, CONSTRUCTION,
             LOGISTICS, CONSULTING, EDUCATION, AUTOMOTIVE, FINANCE,
             ECOMMERCE, WHOLESALE]
currencies: [INR, USD, EUR, GBP]
```

```yaml
# training_config.yaml
models: [logistic_regression, linear_svm, xgboost, random_forest, lightgbm]
ensemble:
  selection_metric: macro_f1
  voting: soft
calibration_method: isotonic
```

---

## 5. Requirements

```
pandas, numpy, scikit-learn, xgboost, lightgbm, joblib,
PyMuPDF, python-docx, Pillow, PaddleOCR,
transformers, sentence-transformers, torch,
matplotlib, seaborn, reportlab
```

---

## 6. Running the Pipeline End to End

```bash
# 1. Generate synthetic dataset (writes dataset/synthetic_data.csv + raw files)
python ml/dataset_generation/generate_documents.py --config config/generation_config.yaml

# 2. Build template-aware train/val/test splits
python ml/splitting/template_aware_split.py

# 3. Preprocess + extract features (cached under features/cache/)
python ml/preprocessing/preprocess.py
python ml/features/feature_builder.py

# 4. Train all base models + ensemble + calibration
python ml/training/train_logistic.py
python ml/training/train_svm.py
python ml/training/train_xgboost.py
python ml/training/train_random_forest.py
python ml/training/train_lightgbm.py
python ml/training/train_ensemble.py
python ml/training/calibrate.py

# 5. Evaluate + auto-generate the PDF metrics report
python ml/evaluation/evaluate.py
# -> writes reports/evaluation_report.pdf, confusion_matrix.png,
#    calibration_curve.png, model_comparison_table.csv, error_analysis.csv

# 6. Run inference
python ml/inference/predict.py --file path/to/document.pdf
```

---

## 7. Design Principles Recap

- **No leakage**: splits are template-aware and company-aware, never a random shuffle over near-duplicate documents.
- **Reusable preprocessing**: identical code path for training and inference — no drift between the two.
- **Calibrated, thresholded confidence**: raw model probabilities are never surfaced directly; thresholds are learned from validation data.
- **OTHER/UNKNOWN as first-class outcomes**: unrelated documents are routed to `OTHER`/human review rather than forced into a known class.
- **Shared classifier first, specialized models only if they win**: Task B models are architected (folders, ground-truth schemas, cached layout features) but only introduced where they outperform the shared approach.
- **Everything reproducible**: every model run produces a versioned PDF report and a versioned metadata.json, so results can be compared across iterations.
