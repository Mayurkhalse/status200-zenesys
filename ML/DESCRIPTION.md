# IntelliParse — ERP Document Classifier Module (ML Service)

## Overview

This repository houses the **Machine Learning Classification & Feature Extraction Engine** for **IntelliParse**, an AI-Powered Document Intelligence Platform for ERP systems.

In the complete IntelliParse architecture (React.js Frontend + FastAPI Orchestrator + AI Agents), this module powers **Step 2 (Document Preprocessing & OCR)** and **Step 3 (Hybrid Document Classification & Decision Routing)**.

---

## Where This Module Fits in the IntelliParse Pipeline

```
[ User Uploads Doc ] ➔ ( React.js Frontend )
                            │
                            ▼
                    ( FastAPI Backend )
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │  INTELLIPARSE ML MODULE (This Repository)    │
     │                                              │
     │  1. Preprocessing & OCR Extraction           │
     │  2. Feature Extraction (TF-IDF + BGE + Layout)│
     │  3. Soft Voting Ensemble Classification      │
     │  4. Isotonic Confidence Calibration          │
     └──────────────────────┬───────────────────────┘
                            │
                            ▼
                ( Classification Routing )
     ┌──────────────────────┼──────────────────────┐
     │                      │                      │
     ▼                      ▼                      ▼
[ AUTO_ACCEPT ]   [ REVIEW / LLM_FALLBACK ]  [ HUMAN_REVIEW ]
(Confidence ≥ 85%)   (60% ≤ Conf < 85%)      (Conf < 60%)
     │                      │                      │
     └──────────────────────┼──────────────────────┘
                            │
                            ▼
         [ Specialized Agents (Task B Extraction) ]
            • Invoice Agent
            • Purchase Order Agent
            • Contract Agent
            • Lead Agent ...
                            │
                            ▼
        [ Action Insights, Risks & Trends Agent ]
                            │
                            ▼
         [ IntelliParse Analytics Dashboard ]
```

---

## How This Repository Powers IntelliParse

### 1. Document Parsing & OCR Preprocessing (Step 2)
- Unified preprocessing engine (`ml/preprocessing/preprocess.py`) handles native PDFs, DOCX files, and scanned image documents (via PyMuPDF, python-docx, and PaddleOCR fallback).
- Outputs standardized text, tokens, and structural layout bounding boxes.

### 2. Hybrid ML Classification Engine (Step 3)
- Evaluates incoming document text and visual features against **14 ERP document classes** (`BUSINESS_INVOICE`, `PURCHASE_ORDER`, `SALES_ORDER`, `QUOTATION`, `PROPOSAL`, `CONTRACT`, `LEAD`, `RECEIPT`, `DELIVERY_NOTE`, `CREDIT_NOTE`, `DEBIT_NOTE`, `PAYMENT_RECEIPT`, `RFQ`, `OTHER`).
- Powered by a calibrated **Soft Voting Ensemble** combining Logistic Regression, Linear SVM, and Random Forest.

### 3. Confidence-Based Decision Routing
Returns calibrated probability scores to drive IntelliParse agent control flow:
- **`AUTO_ACCEPT`** ($\ge 85\%$ confidence): Directly forwards document to the matching specialized extraction agent.
- **`REVIEW / LLM_FALLBACK`** ($60\% \le \text{conf} < 85\%$): Triggers your LLM Fallback Agent for disambiguation.
- **`UNKNOWN / HUMAN_REVIEW`** ($< 60\%$): Routes document to human verification or flags as `OTHER`.

### 4. Task B Architecture Groundwork (Step 4 Integration)
- Caches full document layout features (`features/cache/layout_features.parquet`) and field ground truth schemas (`dataset/extraction_ground_truth/`) so specialized Task B extraction models can be trained without re-parsing documents.

---

## API Integration with IntelliParse FastAPI / React Backend

### Option A: HTTP REST Endpoint
```http
POST http://127.0.0.1:8000/predict/upload
Content-Type: multipart/form-data

file: <document_file>
```

**Response Payload:**
```json
{
  "document_type": "BUSINESS_INVOICE",
  "confidence": 0.9076,
  "decision": "AUTO_ACCEPT",
  "top_k": ["BUSINESS_INVOICE", "DELIVERY_NOTE", "PURCHASE_ORDER"],
  "probabilities": {
    "BUSINESS_INVOICE": 0.9076,
    "PURCHASE_ORDER": 0.0155,
    "DELIVERY_NOTE": 0.0189
  },
  "model_version": "1.0.0"
}
```

### Option B: In-Process Python Import
```python
from ml.inference.predict import predict_document

result = predict_document("uploaded_doc.pdf")
doc_type = result["document_type"]
decision = result["decision"]
```
