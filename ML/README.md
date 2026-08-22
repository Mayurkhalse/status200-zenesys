# ERP Document Classification — ML System

A modular, reproducible ML pipeline that generates synthetic ERP business documents, trains a document-type classifier (Task A), and lays the architecture groundwork for per-document specialized extraction models (Task B).

```
Synthetic Business Documents → Dataset Generation → Preprocessing → Feature Extraction
      → Model Training → Model Evaluation → Best Model Selection
      → Saved Model Files → Inference API
```

---

## 1. Document Classes

```text
BUSINESS_INVOICE   PURCHASE_ORDER   SALES_ORDER   QUOTATION
PROPOSAL           CONTRACT         LEAD          RECEIPT
DELIVERY_NOTE      CREDIT_NOTE      DEBIT_NOTE    PAYMENT_RECEIPT
RFQ                OTHER
```

---

## 2. Quickstart Execution Guide

### Step 1: Install Requirements
```bash
pip install -r requirements.txt
```

### Step 2: Generate Synthetic Dataset
```bash
python ml/dataset_generation/generate_documents.py --config config/generation_config.yaml
```

### Step 3: Partition Train / Validation / Test Splits
```bash
python ml/splitting/template_aware_split.py
```

### Step 4: Preprocess Documents & Build Feature Matrices
```bash
python ml/features/feature_builder.py
```

### Step 5: Train Models & Calibrate Probabilities
```bash
python ml/training/train_logistic.py
python ml/training/train_svm.py
python ml/training/train_xgboost.py
python ml/training/train_random_forest.py
python ml/training/train_lightgbm.py
python ml/training/train_ensemble.py
python ml/training/calibrate.py
```

### Step 6: Evaluate & Auto-Generate 8-Page PDF Report
```bash
python ml/evaluation/evaluate.py
```

### Step 7: Run Single Document Inference
```bash
python ml/inference/predict.py --file dataset/raw/BUSINESS_INVOICE/template_001/doc_000001.pdf
```

### Step 8: Start FastAPI Web Service
```bash
uvicorn api.inference_service:app --reload --port 8000
```

---

## 3. Unit Tests
```bash
pytest tests/
```
