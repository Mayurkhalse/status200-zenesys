# Intelliparse — AI-Powered Document Intelligence for ERP Platforms

> An intelligent document processing pipeline that ingests unstructured business documents, classifies and routes them through specialized AI agents, and surfaces actionable insights, risks, trends, and anomalies on a real-time dashboard.

---

## 🧠 Overview

Modern ERP platforms deal with a flood of unstructured documents — invoices, proposals, leads, purchase orders, contracts, and more — that typically require manual review, tagging, and data entry. **DocIntel** automates this entire lifecycle using a multi-agent AI architecture: from raw document ingestion to OCR/parsing, intelligent classification, specialized field extraction, and finally, high-level business insight generation.

The system is designed to plug into existing ERP workflows, reducing manual document handling while surfacing risks and trends that would otherwise go unnoticed.

---

## 🚀 Key Features

- **Universal Document Ingestion** — Accepts scanned images, PDFs, and digital documents.
- **OCR & Parsing Layer** — Extracts raw text, layout, and structural metadata from documents.
- **Hybrid Classification Agent** — Combines rule-based heuristics, ML models, and LLM fallback to accurately classify documents (Invoice, Proposal, Lead, Purchase Order, etc.), even in ambiguous cases.
- **Specialized Processing Agents** — Document-type-specific agents extract relevant structured data (e.g., line items from invoices, terms from proposals, contact details from leads).
- **Insight & Anomaly Detection Agent** — Analyzes processed data to surface actionable insights, risk flags, trends, and anomalies.
- **Dashboard-Ready Output** — Structured, queryable output designed for visualization in a React-based dashboard.
- **ERP-Friendly Architecture** — Modular pipeline that can be integrated into existing ERP systems via API.

---

## 🏗️ Architecture & Pipeline

```
                ┌────────────────────┐
                │  Document Upload    │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │  OCR / Parsing      │
                │  Layer              │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │ Classification      │
                │ Agent               │
                │ (Rules + ML + LLM)  │
                └─────────┬──────────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
    ┌──────▼─────┐ ┌──────▼─────┐ ┌──────▼─────┐
    │  Invoice    │ │  Proposal   │ │   Lead /    │  ... (more)
    │  Agent      │ │  Agent      │ │   PO Agent  │
    └──────┬─────┘ └──────┬─────┘ └──────┬─────┘
           │              │              │
           └──────────────┼──────────────┘
                          │
                ┌─────────▼──────────┐
                │ Insight Agent       │
                │ (Actions, Risks,    │
                │  Trends, Anomalies) │
                └─────────┬──────────┘
                          │
                ┌─────────▼──────────┐
                │  Dashboard (React)  │
                └────────────────────┘
```

### Pipeline Stages

1. **Document Upload** — User uploads a document via the frontend or an API endpoint.
2. **Parsing (OCR)** — The document is parsed to extract raw text, tables, and layout metadata.
3. **Classification Agent** — A hybrid rule-based + ML + LLM-fallback agent determines the document type (Invoice, Proposal, Lead, Purchase Order, etc.).
4. **Specialized Agents** — Based on classification, the document is routed to a domain-specific agent that extracts structured fields relevant to that document type.
5. **Insight Agent** — Aggregates outputs across documents to detect actionable insights, risks, trends, and anomalies.
6. **Dashboard** — All processed data and insights are visualized for end users.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | **React.js** |
| Backend / API | **FastAPI** |
| Document Parsing | OCR engine (e.g., Tesseract / cloud OCR) |
| Classification | Rule-based logic + ML model + LLM fallback |
| Specialized Extraction | Domain-specific agents (per document type) |
| Insight Generation | LLM-based analytics agent |

---

## 📂 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI routes
│   │   ├── ocr/                # Document parsing & OCR pipeline
│   │   ├── classification/     # Rule-based + ML + LLM classifier
│   │   ├── agents/              # Specialized document agents
│   │   │   ├── invoice_agent.py
│   │   │   ├── proposal_agent.py
│   │   │   ├── lead_agent.py
│   │   │   └── purchase_order_agent.py
│   │   ├── insights/            # Insight/risk/anomaly detection agent
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── package.json
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup (React)

```bash
cd frontend
npm install
npm run dev
```

The frontend will typically run on `http://localhost:5173` (or `3000`) and the backend on `http://localhost:8000`.

---

## 🔄 Document Classification Categories

| Category | Description |
|---|---|
| Invoice | Billing documents with line items, amounts, tax details |
| Proposal | Business proposals with terms, scope, pricing |
| Lead | Prospective client/contact information |
| Purchase Order | Order requests with vendor, quantity, and pricing details |
| *(Extendable)* | New categories can be added by extending the classifier and adding a new specialized agent |

---

## 📊 Insight Agent Outputs

The final insight agent generates:

- **Actionable Insights** — Recommended next steps based on document content.
- **Risk Flags** — Potential compliance, financial, or contractual risks.
- **Trend Analysis** — Patterns across documents over time (e.g., spending trends, lead volume).
- **Anomaly Detection** — Outliers or inconsistencies flagged for review.

These outputs are consumed by the React dashboard for visualization.

---

## 🗺️ Roadmap

- [ ] Add support for additional document types
- [ ] Improve LLM fallback accuracy with fine-tuned prompts
- [ ] Add authentication & role-based access control
- [ ] Add export functionality (CSV/PDF reports from dashboard)
- [ ] Integrate with third-party ERP systems (SAP, Zoho, etc.)

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.

---

## 📄 License

This project is licensed under the MIT License — see the `LICENSE` file for details.
