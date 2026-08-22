# IntelliParse

**AI-Powered Document Intelligence Platform for ERP Systems**

IntelliParse is an intelligent document processing platform designed to plug into ERP ecosystems. It ingests unstructured documents (invoices, proposals, leads, purchase orders, and more), extracts structured data, classifies documents automatically, routes them to specialized processing agents, and surfaces actionable insights, risks, trends, and anomalies through an interactive dashboard. Extracted data is written to a shared database that also powers a **Mock ERP UI**, demonstrating how pipeline output integrates into a real ERP system alongside its existing records.

> **MVP scope decisions** (locked in for this build — see inline notes throughout):
> - **File storage:** local disk (`backend/storage/uploads/`), not S3 — swap-in-ready via an abstracted storage interface.
> - **Auth:** simple JWT (email + password, access + refresh tokens). No MFA/OAuth for MVP.
> - **Deployment:** local dev only. No Docker/K8s config in this pass — flagged as roadmap.
> - **Insight Agent:** LLM-judged risk/anomaly detection (not rule-based thresholds or pure statistics).
> - **Encryption at rest:** field-level AES-256-GCM for sensitive MongoDB fields + AES-256-GCM whole-file encryption for disk-stored uploads.
> - **Failure handling:** OCR/LLM calls retry 2–3x with exponential backoff, then route to `HUMAN_REVIEW` with a logged error reason.
> - **Testing/CI:** noted as a roadmap item only — not built out in this pass.

---

## ✨ Overview

Enterprises deal with a constant influx of unstructured documents — invoices, purchase orders, proposals, lead forms, contracts, and more. Manually reading, classifying, and extracting data from these documents is slow, error-prone, and doesn't scale.

IntelliParse automates this entire pipeline using a combination of OCR, rule-based logic, machine learning, and LLM-powered agents — turning raw documents into structured, actionable business intelligence that integrates directly with ERP workflows.

---

## 🏗️ Architecture / Pipeline

```
┌──────────────────┐
│  1. Document      │
│     Upload        │
└─────────┬─────────┘
          ▼
┌───────────────────────────────┐
│  2. Preprocessing & OCR         │
│     PyMuPDF / python-docx /     │
│     PaddleOCR + Layout Parsing  │
└─────────┬──────────────────────┘
          ▼
┌───────────────────────────────┐
│  3. Classification Agent       │
│     Rule-based + ML + LLM      │
│     (run in parallel)          │
│  → Confidence-Based Routing    │
└─────────┬──────────────────────┘
          ▼
┌──────────────────┐
│  4. Specialized   │
│     Agents        │
└─────────┬─────────┘
          ▼
┌───────────────────────────────┐
│  5. Insight Agent (LLM-judged)  │
│     Risk / Anomaly / Trend /    │
│     Recommendation Detection    │
└─────────┬──────────────────────┘
          ▼
┌───────────────────────────────┐
│  6. Dashboard                   │
└─────────┬──────────────────────┘
          ▼
┌───────────────────────────────┐
│  7. RAG Chatbot                 │
└─────────┬──────────────────────┘
          ▼
┌───────────────────────────────┐
│  Shared Database (MongoDB)      │
└─────────┬──────────────────────┘
    ┌─────┴──────┐
    ▼             ▼
┌────────────┐ ┌────────────────┐
│ Document    │ │ Mock ERP UI     │
│ Dashboard   │ │                 │
└────────────┘ └────────────────┘
```

### Pipeline Stages

1. **Document Upload** — file is validated, encrypted, and written to local disk storage; a `documents` record is created.
2. **Preprocessing & OCR** — routed by format: **PyMuPDF** (PDF), **python-docx** (DOCX), **PaddleOCR** (scanned images/PDFs). Layout features cached.
3. **Classification Agent** — rule-based, ML (soft-voting ensemble), and LLM classifiers run in parallel; confidence-based routing into 14 ERP document classes.
4. **Specialized Agents** — per-type structured field extraction (hybrid rules + LLM).
5. **Insight Agent** — **LLM-judged** risk, anomaly, trend, and recommendation detection using document context + vendor/entity history (see [Insight Agent](#-insight-agent-llm-judged-risk--anomaly-detection) below).
6. **Dashboard** — recommendations, risk flags, anomaly alerts.
7. **RAG Chatbot** — hybrid semantic (pgvector) + keyword search.
8. **Shared Database (MongoDB)** — single source of truth for pipeline output + Mock ERP data.
9. **Two UIs** — Document Intelligence Dashboard + Mock ERP UI, both reading the same data, refreshed on page load/batch.

---

## 🧰 Tech Stack

| Layer               | Technology       |
|---------------------|-----------------|
| Frontend            | React.js (Vite) + React Router + TanStack Query |
| Backend / API        | FastAPI (Python) |
| Document Parsing    | PyMuPDF (PDF) · python-docx (DOCX) · PaddleOCR (images/scans) |
| Classification       | Rule-based + ML (Soft Voting Ensemble: Logistic Regression, Linear SVM, Random Forest) + LLM, parallel, confidence-routed |
| Specialized Agents   | Hybrid: layout-aware rules + regex + LLM extraction, per document type |
| Insight Generation   | LLM-powered Agent (LLM-judged risk/anomaly/trend detection) |
| Dashboard / Mock ERP | React.js |
| Primary Database     | MongoDB |
| Vector Store / RAG   | pgvector (PostgreSQL extension) |
| Embedding Model       | `sentence-transformers/all-MiniLM-L6-v2` (free, open-source, 384-dim) |
| File Storage          | Local disk (`backend/storage/uploads/`), AES-256-GCM encrypted at rest |
| Auth                   | JWT (access + refresh tokens), no MFA/OAuth for MVP |
| ML Service            | Python (scikit-learn, PaddleOCR, PyMuPDF) |

---

## 📂 Project Structure

```
zenesys/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── extracted_documents.py
│   │   │   │   ├── insights.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── erp.py
│   │   │   │   ├── chat.py
│   │   │   │   └── users.py
│   │   ├── core/
│   │   │   ├── config.py            # env/settings
│   │   │   ├── security.py          # JWT issue/verify, password hashing
│   │   │   ├── encryption.py        # AES-256-GCM field + file encryption
│   │   │   └── rbac.py              # role/permission checks
│   │   ├── classification/
│   │   ├── agents/
│   │   │   ├── specialized/
│   │   │   │   ├── prompts/         # <type>_extraction.txt (14 files)
│   │   │   │   ├── invoice_agent.py
│   │   │   │   ├── purchase_order_agent.py
│   │   │   │   └── ... (one per document type)
│   │   │   ├── insights/
│   │   │   │   ├── prompts/
│   │   │   │   │   └── insight_agent.txt
│   │   │   │   └── insight_agent.py
│   │   │   └── rag_chatbot/
│   │   ├── retrieval/
│   │   │   ├── embeddings/
│   │   │   ├── semantic_search/
│   │   │   └── keyword_search/
│   │   ├── mock_erp/
│   │   │   ├── api/
│   │   │   └── seed/
│   │   ├── models/
│   │   │   └── schemas/             # Pydantic schema per document type
│   │   ├── storage/
│   │   │   └── uploads/             # local encrypted file storage (gitignored)
│   │   └── services/
│   ├── tests/                        # roadmap — see Testing & CI
│   └── requirements.txt
│
├── frontend/                        # Document Intelligence Dashboard
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/                # API client (axios/fetch wrapper)
│   │   └── dashboard/
│   └── package.json
│
├── ML/
│   ├── api/
│   ├── config/
│   ├── dataset/
│   │   └── extraction_ground_truth/
│   ├── features/
│   │   └── cache/
│   ├── ml/
│   │   ├── preprocessing/
│   │   └── inference/
│   ├── models/
│   ├── reports/
│   ├── tests/
│   ├── DESCRIPTION.md
│   ├── DETAILS.md
│   ├── README.md
│   └── requirements.txt
│
├── mock-erp-frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
│
├── docs/
├── .gitignore
└── README.md
```

---

## 🔌 REST API Contract

All routes are prefixed `/api`. All routes except `/api/auth/*` require `Authorization: Bearer <access_token>` and are checked against RBAC (see [Auth & Security](#-auth--security)).

### Auth

| Method | Path | Body | Response | Notes |
|---|---|---|---|---|
| `POST` | `/api/auth/register` | `{email, password, full_name, role}` | `{user_id, email, role}` | `role` restricted to `admin`-creatable in production; open for MVP seeding |
| `POST` | `/api/auth/login` | `{email, password}` | `{access_token, refresh_token, token_type: "bearer", expires_in}` | See [JWT spec](#jwt-structure--expiry) |
| `POST` | `/api/auth/refresh` | `{refresh_token}` | `{access_token, refresh_token, expires_in}` | Rotates refresh token |
| `POST` | `/api/auth/logout` | `{refresh_token}` | `204 No Content` | Revokes refresh token |
| `GET` | `/api/users/me` | — | `{user_id, email, full_name, role}` | Current session identity |

### Documents

| Method | Path | Body / Query | Response | Notes |
|---|---|---|---|---|
| `POST` | `/api/documents/upload` | `multipart/form-data: file` | `{document_id, status: "uploaded"}` | Encrypts + stores file, kicks off async pipeline |
| `GET` | `/api/documents` | `?status=&document_type=&date_from=&date_to=&page=&limit=` | `{items: [...], total, page, limit}` | List/filter |
| `GET` | `/api/documents/{document_id}` | — | Full `documents` record | Includes classification result |
| `GET` | `/api/documents/{document_id}/status` | — | `{status, decision, error}` | Lightweight polling endpoint for upload progress |
| `DELETE` | `/api/documents/{document_id}` | — | `204 No Content` | Soft-delete; logged to `audit_logs` |

### Extracted Documents

| Method | Path | Body | Response | Notes |
|---|---|---|---|---|
| `GET` | `/api/extracted-documents/{document_id}` | — | Full `extracted_documents` record | Includes `field_confidences`, `needs_review` |
| `PATCH` | `/api/extracted-documents/{document_id}` | `{fields: {...}}` | Updated record | Human-review correction; logged to `audit_logs` (`action: edit`) |

### Insights

| Method | Path | Query / Body | Response | Notes |
|---|---|---|---|---|
| `GET` | `/api/insights` | `?type=&severity=&status=&related_document_id=&date_from=&date_to=&page=&limit=` | `{items: [...], total}` | Powers risk feed + recommendations feed |
| `PATCH` | `/api/insights/{insight_id}` | `{status: "acknowledged"\|"resolved"}` | Updated record | |

### Dashboard

| Method | Path | Query | Response | Notes |
|---|---|---|---|---|
| `GET` | `/api/dashboard/kpis` | `?date_from=&date_to=` | `{volume, classification_health, risk_summary, processing_performance}` | Aggregated KPI payload, see [Dashboard Parameters](#dashboard-parameters) |
| `GET` | `/api/dashboard/trends` | `?metric=spend_by_vendor\|volume_by_type&date_from=&date_to=` | `{series: [...]}` | Chart data |

### Mock ERP

| Method | Path | Query / Body | Response | Notes |
|---|---|---|---|---|
| `GET` | `/api/erp/records` | `?record_type=&erp_status=&source=&page=&limit=` | `{items: [...], total}` | |
| `GET` | `/api/erp/records/{record_id}` | — | Full `erp_records` record | Includes `status_history` |
| `PATCH` | `/api/erp/records/{record_id}/status` | `{new_status: "pending_approval"\|"approved"\|"paid"\|"rejected"}` | Updated record | Manual workflow transition; appends to `status_history`; logged to `audit_logs` (`action: erp_write`) |
| `POST` | `/api/erp/seed` | `{count_per_type: int}` | `{seeded: int}` | **Dev-only**, disabled outside local env |

### Chatbot

| Method | Path | Body | Response | Notes |
|---|---|---|---|---|
| `POST` | `/api/chat/sessions` | — | `{session_id}` | Creates a session scoped to current user |
| `GET` | `/api/chat/sessions/{session_id}` | — | Full `chat_sessions` record | |
| `POST` | `/api/chat/sessions/{session_id}/messages` | `{content}` | `{role: "assistant", content, source_document_ids, retrieval_method}` | Runs hybrid retrieval filtered to user's RBAC scope |

### ML Service (standalone, port 8001)

| Method | Path | Body | Response |
|---|---|---|---|
| `POST` | `/predict/upload` | `multipart/form-data: file` | `{document_type, confidence, decision, top_k, probabilities, model_version}` |

**Standard error shape** (all endpoints):
```json
{
  "error": {
    "code": "string (e.g. VALIDATION_ERROR, NOT_FOUND, FORBIDDEN, PIPELINE_FAILED)",
    "message": "string",
    "detail": "object | null"
  }
}
```

---

## 🖥️ Frontend Architecture

### Document Intelligence Dashboard (`frontend/`)

| Route | Page | Key Components |
|---|---|---|
| `/login` | Login | `LoginForm` |
| `/` | Overview | `KpiCards`, `VolumeChart`, `ClassificationHealthWidget`, `RecentActivityFeed` |
| `/documents` | Documents List | `DocumentTable` (filter/sort/paginate), `StatusBadge`, `UploadModal` |
| `/documents/:id` | Document Detail | `DocumentPreview`, `ClassificationPanel`, `ExtractedFieldsForm` (editable, calls `PATCH /extracted-documents`), `ConfidenceIndicator`, `LinkedInsightsList` |
| `/insights` | Risk & Anomaly Feed | `InsightList` (filter by type/severity/status), `InsightCard`, `AcknowledgeResolveButtons` |
| `/recommendations` | Recommendations Feed | `RecommendationList`, `RecommendationCard` |
| `/trends` | Business Trends | `SpendByVendorChart`, `VolumeByTypeChart` |
| `/chat` | RAG Chatbot | `ChatWindow`, `MessageBubble` (with `SourceCitationLink`), `SessionSidebar` |
| `/settings` | Profile / Settings | `ProfileForm` |

`services/api.js` wraps all `/api/*` calls above; `services/auth.js` handles token storage (in-memory + refresh interception) and attaches `Authorization` headers.

### Mock ERP UI (`mock-erp-frontend/`)

| Route | Page | Key Components |
|---|---|---|
| `/login` | Login (shared auth) | `LoginForm` |
| `/records` | ERP Records List | `RecordTable` (filter by `record_type`, `erp_status`, `source`), `SourceBadge` (`Mock Seed Data` vs `Pipeline-Generated`) |
| `/records/:id` | Record Detail | `RecordSummary`, `StatusHistoryTimeline`, `WorkflowActionButtons` (`Approve`, `Reject`, `Mark Paid`, calling `PATCH /erp/records/:id/status`), `LinkedDocumentLink` (jumps to Dashboard's document detail if `source: pipeline`) |

Both frontends share the same `Authorization` bearer token once logged in (single SSO-lite session across both apps, since they hit the same backend).

---

## 🔐 Auth & Security

### JWT Structure & Expiry

- **Access token:** JWT, `HS256`, 15-minute expiry. Payload: `{sub: user_id, email, role, iat, exp}`.
- **Refresh token:** opaque random token (not a JWT), 7-day expiry, stored hashed in a `refresh_tokens` collection (`{token_hash, user_id, expires_at, revoked: bool}`). Rotated on every use (old token revoked, new one issued) to limit replay risk.
- **No MFA/OAuth for MVP** — email + password only, hashed with `bcrypt`.
- **Token transport:** `Authorization: Bearer <access_token>` header (not cookies, to keep both frontends simple SPA clients).
- **RBAC roles (MVP):** `admin`, `analyst`, `viewer`. Enforced per-request in `core/rbac.py` via a FastAPI dependency on every protected route — see original Security section's Authorization principle (checked every call, not just at login).

### Data Encryption

- **In transit:** HTTPS/TLS (dev: self-signed/local; note as roadmap for prod certs).
- **At rest — files:** each uploaded file is encrypted with **AES-256-GCM** (random 96-bit nonce per file) immediately on upload, before any OCR/parsing touches it. Stored at `backend/storage/uploads/{document_id}.enc`. Decrypted only in-memory during processing, never re-written to disk in plaintext, and the in-memory buffer is discarded after the pipeline stage completes.
- **At rest — database:** sensitive fields (PII, financial amounts, contact info) in `extracted_documents.fields` and `erp_records` are encrypted **field-level** with AES-256-GCM before being written to MongoDB. Non-sensitive metadata (status, timestamps, IDs) stays in plaintext for queryability.
- **Key management (MVP):** a single symmetric master key held in `KMS_KEY_ID` env var, used to derive per-record data keys (envelope-encryption pattern). **Roadmap:** swap the env-var master key for a real KMS (AWS KMS / GCP KMS) without changing the envelope-encryption call sites — `core/encryption.py` is written against a `KeyProvider` interface for exactly this reason.

### PII Redaction Before LLM Calls

Before any text reaches an LLM (classification fallback, specialized extraction, insight agent, chatbot indexing), a redaction pass masks sensitive spans (emails, phone numbers, personal names, bank/account numbers) with placeholder tokens (e.g. `[EMAIL_1]`). The token→real-value mapping is stored encrypted (`documents.pii_redaction_map_ref`) and only used server-side to re-map LLM output back to real values before writing to `extracted_documents`. Only `admin`/`analyst` roles see re-mapped values in API responses; `viewer` role sees masked values.

### File Validation

Uploads are checked for MIME type (`application/pdf`, `.docx`, `image/png`, `image/jpeg` only), max size (default 25MB, configurable), and basic content sniffing (magic bytes) before being accepted — rejects mismatched extensions and obvious non-document payloads.

---

## ⚠️ Error Handling & Retry Policy

Applies to every external/expensive call in the pipeline: PaddleOCR invocation, LLM classification fallback, LLM specialized-field extraction, LLM insight generation, and LLM chatbot generation.

| Step | Behavior |
|---|---|
| **Retry count** | 2–3 attempts (configurable via `PIPELINE_MAX_RETRIES`, default `3`) |
| **Backoff** | Exponential: 2s → 4s → 8s between attempts |
| **On exhaustion** | Document `status` is set to `HUMAN_REVIEW`; an `error` field is populated on the `documents` record with `{stage, message, attempts}`; an `audit_logs` entry is written (`action: pipeline_error`) |
| **Classification ties** (two classes within a small confidence margin, e.g. <2%) | Routed to `REVIEW_LLM_FALLBACK` regardless of the raw top score, so the LLM disambiguates rather than silently picking the higher of two near-equal scores |
| **OCR total failure** (unreadable scan, corrupt file) | Document `status: failed`, surfaced in the Dashboard's document list with a retry-upload action available to the user; not silently dropped |
| **Partial extraction** (some fields extracted, others fail) | Document still proceeds to `extracted_documents` with `needs_review: true`; failed fields are `null` with a `field_confidences` entry of `0.0`, not blocked entirely |
| **Insight Agent failure** | Non-blocking — a failed insight generation does not roll back or block the document's `extracted_documents`/`erp_records` write; it's logged and retried on next scheduled reconciliation pass (roadmap: a lightweight sweep job for documents missing insights) |

---

## 🧠 Insight Agent (LLM-Judged Risk & Anomaly Detection)

Runs once per newly ingested document, immediately after extraction (Stage 5), not as a batch job.

### How it decides what's a risk/anomaly

1. **Context assembly** — pulls the new document's `extracted_documents.fields`, plus recent history for the same `related_entity` (vendor/customer/lead name): last 10 `erp_records`/`extracted_documents` for that entity, aggregate stats (avg spend, avg days-to-pay, document frequency).
2. **LLM call** — the assembled context is sent to the LLM with the prompt template below, which **requires strict JSON output** matching the `insights` schema. The model is asked to reason over the data (not just pattern-match) and produce zero or more insight objects.
3. **Schema validation** — output is validated against the `insights` Pydantic schema; malformed responses are retried (see [Error Handling](#-error-handling--retry-policy)); if still malformed after retries, no insight is written for that document (fails open, not silently fabricated).
4. **Write** — valid insights are written to the `insights` collection, each linked to the triggering document(s).

### Insight Agent prompt template (`backend/app/agents/insights/prompts/insight_agent.txt`)

```
You are a financial and operational risk analyst reviewing business documents for an ERP system.

You will be given:
1. The newly processed document's extracted structured data.
2. Recent historical records for the same vendor/customer/lead ("related_entity"), including aggregate stats.

Your job is to identify any RISKS, ANOMALIES, TRENDS, or RECOMMENDATIONS worth surfacing to a
business user. Only flag things that are genuinely notable — do not invent findings if the data
looks normal. It is correct to return an empty list.

Consider (not an exhaustive checklist, use judgment):
- Unusual spend compared to this entity's history (spikes, drops, round-number anomalies)
- Payment terms or amounts that deviate from this entity's past pattern
- Possible duplicate documents (same entity, similar amount, close dates)
- Overdue or approaching-due-date items needing attention
- Missing or inconsistent required fields that suggest data quality risk
- Multi-document trends (e.g. a vendor's invoice frequency climbing steadily)

NEW DOCUMENT (type: {document_type}):
{extracted_fields_json}

RECENT HISTORY FOR "{related_entity}" (last {n} records):
{history_json}

AGGREGATE STATS FOR "{related_entity}":
{aggregate_stats_json}

Respond with ONLY a JSON array (no prose, no markdown fences). Each element must match:
{
  "type": "risk" | "anomaly" | "trend" | "recommendation",
  "severity": "low" | "medium" | "high" | "critical",
  "title": "string, under 80 chars",
  "description": "string, 1-3 sentences, plain language for a business user",
  "related_entity": "string"
}

If nothing is notable, respond with: []
```

---

## 📝 Specialized Agent Extraction Prompt Templates

All templates live at `backend/app/agents/specialized/prompts/<type>_extraction.txt`. **These operate on PII-redacted text** (masked tokens like `[EMAIL_1]`, `[PHONE_1]`, `[PERSON_1]` are preserved as-is in output; the backend re-maps them after the LLM call). Every template follows the same shape: role framing, the type's JSON schema, the redacted OCR/text input, and a strict "JSON only" output instruction.

### `business_invoice_extraction.txt`
```
You are a document extraction agent specialized in BUSINESS INVOICES.
Extract the following fields from the text below. Use null for any field you cannot find —
do not guess or fabricate values. Some personal/contact data may appear as masked tokens
(e.g. [EMAIL_1]) — preserve these tokens exactly as-is in your output, do not attempt to unmask them.

Required JSON schema:
{
  "invoice_number": "string | null",
  "vendor": "string | null",
  "bill_to": "string | null",
  "issue_date": "YYYY-MM-DD | null",
  "due_date": "YYYY-MM-DD | null",
  "line_items": [{"description": "string", "qty": "number", "unit_price": "number", "amount": "number"}],
  "subtotal": "number | null",
  "tax": "number | null",
  "total": "number | null",
  "currency": "string | null (ISO 4217, e.g. USD)",
  "payment_terms": "string | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `purchase_order_extraction.txt`
```
You are a document extraction agent specialized in PURCHASE ORDERS.
Extract the following fields. Use null where not found. Preserve any masked tokens (e.g. [EMAIL_1]) as-is.

Required JSON schema:
{
  "po_number": "string | null",
  "vendor": "string | null",
  "buyer": "string | null",
  "order_date": "YYYY-MM-DD | null",
  "delivery_date": "YYYY-MM-DD | null",
  "line_items": [{"description": "string", "qty": "number", "unit_price": "number", "amount": "number"}],
  "total": "number | null",
  "currency": "string | null",
  "status": "string | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `sales_order_extraction.txt`
```
You are a document extraction agent specialized in SALES ORDERS.
Extract the following fields. Use null where not found. Preserve any masked tokens as-is.

Required JSON schema:
{
  "so_number": "string | null",
  "customer": "string | null",
  "salesperson": "string | null",
  "order_date": "YYYY-MM-DD | null",
  "expected_shipment_date": "YYYY-MM-DD | null",
  "line_items": [{"description": "string", "qty": "number", "unit_price": "number", "amount": "number"}],
  "total": "number | null",
  "currency": "string | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `quotation_extraction.txt`
```
You are a document extraction agent specialized in QUOTATIONS.
Extract the following fields. Use null where not found. Preserve any masked tokens as-is.

Required JSON schema:
{
  "quote_number": "string | null",
  "client": "string | null",
  "issue_date": "YYYY-MM-DD | null",
  "valid_until": "YYYY-MM-DD | null",
  "line_items": [{"description": "string", "qty": "number", "unit_price": "number", "amount": "number"}],
  "total": "number | null",
  "currency": "string | null",
  "terms": "string | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `proposal_extraction.txt`
```
You are a document extraction agent specialized in BUSINESS PROPOSALS.
Extract the following fields. Use null where not found. Preserve any masked tokens as-is.
"scope_summary" should be a concise 2-4 sentence summary in your own words, not a verbatim copy.

Required JSON schema:
{
  "proposal_id": "string | null",
  "client": "string | null",
  "submitted_by": "string | null",
  "submission_date": "YYYY-MM-DD | null",
  "scope_summary": "string | null",
  "estimated_value": "number | null",
  "validity_date": "YYYY-MM-DD | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `contract_extraction.txt`
```
You are a document extraction agent specialized in CONTRACTS.
Extract the following fields. Use null where not found. Preserve any masked tokens as-is.
For "key_clauses", identify distinct clauses (e.g. termination, liability, confidentiality,
payment, renewal) and summarize each in 1-2 sentences — do not reproduce clause text verbatim.

Required JSON schema:
{
  "contract_id": "string | null",
  "parties": ["string"],
  "effective_date": "YYYY-MM-DD | null",
  "expiry_date": "YYYY-MM-DD | null",
  "contract_value": "number | null",
  "key_clauses": [{"clause_type": "string", "summary": "string"}],
  "renewal_terms": "string | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `lead_extraction.txt`
```
You are a document extraction agent specialized in SALES LEADS.
Extract the following fields. Use null where not found. Preserve any masked tokens
(e.g. [EMAIL_1], [PHONE_1]) exactly as-is — do not attempt to unmask them.

Required JSON schema:
{
  "lead_name": "string | null",
  "company": "string | null",
  "contact_email": "string | null",
  "contact_phone": "string | null",
  "source": "string | null",
  "interest": "string | null",
  "status": "string | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `receipt_extraction.txt`
```
You are a document extraction agent specialized in RECEIPTS.
Extract the following fields. Use null where not found. Preserve any masked tokens as-is.

Required JSON schema:
{
  "receipt_number": "string | null",
  "merchant": "string | null",
  "transaction_date": "YYYY-MM-DD | null",
  "line_items": [{"description": "string", "qty": "number", "unit_price": "number", "amount": "number"}],
  "total": "number | null",
  "payment_method": "string | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `delivery_note_extraction.txt`
```
You are a document extraction agent specialized in DELIVERY NOTES.
Extract the following fields. Use null where not found. Preserve any masked tokens as-is.

Required JSON schema:
{
  "delivery_note_number": "string | null",
  "linked_po_number": "string | null",
  "vendor": "string | null",
  "delivery_date": "YYYY-MM-DD | null",
  "line_items": [{"description": "string", "qty_shipped": "number"}],
  "received_by": "string | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `credit_note_extraction.txt`
```
You are a document extraction agent specialized in CREDIT NOTES.
Extract the following fields. Use null where not found. Preserve any masked tokens as-is.

Required JSON schema:
{
  "credit_note_number": "string | null",
  "linked_invoice_number": "string | null",
  "vendor": "string | null",
  "issue_date": "YYYY-MM-DD | null",
  "credit_amount": "number | null",
  "reason": "string | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `debit_note_extraction.txt`
```
You are a document extraction agent specialized in DEBIT NOTES.
Extract the following fields. Use null where not found. Preserve any masked tokens as-is.

Required JSON schema:
{
  "debit_note_number": "string | null",
  "linked_invoice_number": "string | null",
  "vendor": "string | null",
  "issue_date": "YYYY-MM-DD | null",
  "debit_amount": "number | null",
  "reason": "string | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `payment_receipt_extraction.txt`
```
You are a document extraction agent specialized in PAYMENT RECEIPTS.
Extract the following fields. Use null where not found. Preserve any masked tokens as-is.

Required JSON schema:
{
  "receipt_number": "string | null",
  "linked_invoice_number": "string | null",
  "payer": "string | null",
  "payment_date": "YYYY-MM-DD | null",
  "amount_paid": "number | null",
  "payment_method": "string | null",
  "remaining_balance": "number | null"
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `rfq_extraction.txt`
```
You are a document extraction agent specialized in REQUESTS FOR QUOTATION (RFQ).
Extract the following fields. Use null where not found. Preserve any masked tokens as-is.

Required JSON schema:
{
  "rfq_number": "string | null",
  "requester": "string | null",
  "issue_date": "YYYY-MM-DD | null",
  "response_deadline": "YYYY-MM-DD | null",
  "line_items": [{"description": "string", "qty_requested": "number"}]
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

### `other_extraction.txt`
```
You are a document triage agent. This document did not confidently match any of the 14
known ERP document types and has been routed to HUMAN_REVIEW. Your job is only to summarize
it, not to force it into a schema.

Required JSON schema:
{
  "raw_text_summary": "string, 2-4 sentence plain-language summary of what this document appears to be",
  "detected_keywords": ["string, notable terms/entities found, up to 10"]
}

DOCUMENT TEXT:
{redacted_text}

Respond with ONLY the JSON object, no prose, no markdown fences.
```

---

## 🚀 Features

- 📄 **Multi-format document ingestion** — PDFs, DOCX, scanned images, and more
- 🔍 **OCR-powered parsing** — PyMuPDF, python-docx, and PaddleOCR
- 🧠 **Hybrid classification engine** — Rule-based + ML + LLM, confidence-routed across 14 ERP document classes
- 🤖 **Specialized processing agents** — Tailored extraction per document type, full prompt templates above
- 📊 **AI-driven insights** — LLM-judged risk, anomaly, trend, and recommendation detection
- 📈 **Interactive dashboard** — KPIs, risk/anomaly widgets, recommendations feed
- 💬 **RAG-powered chatbot** — Hybrid semantic + keyword search, per-user RBAC-scoped
- 🔗 **ERP-ready integration** — Mock ERP UI backed by the same shared database

---

## 🔍 OCR & Preprocessing Pipeline

Lives in `ML/ml/preprocessing/`.

### 1. Document Format Routing (`preprocess.py`)

```
[ Incoming Document ]
        │
┌───────┼────────────────────┐
▼                             ▼                       ▼
.pdf File               .docx File            .png / .jpg Image
│                             │                       │
▼                             ▼                       ▼
PyMuPDF Direct Text      python-docx Native      PaddleOCR Engine
& BBox Extraction        Paragraph/Table Text     (ml/preprocessing/ocr.py)
```

- **Digital PDFs** — PyMuPDF, instant text + layout blocks.
- **Word Documents** — python-docx, paragraphs + tables.
- **Scanned Images/PDFs** — PaddleOCR.

### 2. The OCR Engine (`ocr.py`)

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
result = ocr.ocr(image_path, cls=True)
```

Extracts angle/skew correction, bounding boxes, and text + confidence scores.

### 3. Layout Bounding Box Integration (`extract_layout.py`)

Computes header/footer/column detection, cached to `features/cache/layout_features.parquet` for reuse by Specialized Agents.

---

## 🧠 ML Classification Engine

### Document Classes (14)
`BUSINESS_INVOICE`, `PURCHASE_ORDER`, `SALES_ORDER`, `QUOTATION`, `PROPOSAL`, `CONTRACT`, `LEAD`, `RECEIPT`, `DELIVERY_NOTE`, `CREDIT_NOTE`, `DEBIT_NOTE`, `PAYMENT_RECEIPT`, `RFQ`, `OTHER`.

### Hybrid Ensemble Model
Calibrated **Soft Voting Ensemble** (Logistic Regression, Linear SVM, Random Forest) + rule-based checks + LLM classifier, running in **parallel**.

### Confidence-Based Decision Routing

| Decision | Confidence Range | Action |
|---|---|---|
| `AUTO_ACCEPT` | ≥ 85% | Forwarded to matching Specialized Agent |
| `REVIEW / LLM_FALLBACK` | 60% ≤ conf < 85%, **or top-2 classes within 2% of each other** | LLM classifier disambiguates |
| `HUMAN_REVIEW` | < 60% | Routed to human verification / flagged `OTHER` |

### API Integration

**Option A — HTTP:**
```http
POST http://127.0.0.1:8001/predict/upload
Content-Type: multipart/form-data
file: <document_file>
```
```json
{
  "document_type": "BUSINESS_INVOICE",
  "confidence": 0.9076,
  "decision": "AUTO_ACCEPT",
  "top_k": ["BUSINESS_INVOICE", "DELIVERY_NOTE", "PURCHASE_ORDER"],
  "probabilities": {"BUSINESS_INVOICE": 0.9076, "PURCHASE_ORDER": 0.0155, "DELIVERY_NOTE": 0.0189},
  "model_version": "1.0.0"
}
```

**Option B — In-process:**
```python
from ml.inference.predict import predict_document
result = predict_document("uploaded_doc.pdf")
```

---

## ⚙️ Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn
- MongoDB instance
- PostgreSQL instance with `pgvector` enabled

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### ML Service Setup
```bash
cd ML
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8001
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Mock ERP Frontend Setup
```bash
cd mock-erp-frontend
npm install
npm start
```

### Environment Variables

`backend/.env`:
```env
MONGODB_URI=
POSTGRES_URI=
LLM_API_KEY=
SECRET_KEY=              # JWT signing secret
KMS_KEY_ID=               # MVP: env-var master key for envelope encryption; roadmap: real KMS
UPLOAD_DIR=./storage/uploads
PIPELINE_MAX_RETRIES=3
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> **Deployment:** local dev only for this MVP pass — no Dockerfile/Compose/K8s config included. Flagged in [Roadmap](#-roadmap) for a later pass once the app is functionally complete.

---

## 💬 RAG Chatbot (Document Q&A)

*(unchanged from original — see [Data Model](#-data-model) for `chat_sessions` and `document_embeddings` schemas)*

- **Embedding-based Semantic Search (pgvector)** via `sentence-transformers/all-MiniLM-L6-v2` (384-dim, free, open-source).
- **Keyword / Key-Value Matching** over extracted structured fields in MongoDB for precise lookups.
- **Hybrid Ranking** merges both result sets.
- **Source Grounding** — every answer cites originating document(s).
- **Per-User Session Scoping** — retrieval filtered to the requesting user's RBAC role via `POST /api/chat/sessions/{id}/messages`.

Upgrade path if retrieval quality needs improvement: `BAAI/bge-base-en-v1.5` (768-dim) — re-embed + update `VECTOR()` dimension.

---

## 🏭 Mock ERP Integration

- Seeded via `POST /api/erp/seed` (dev-only) with realistic mock records.
- Pipeline output is **appended** to `erp_records` (`source: pipeline`) — no separate silo.
- Both UIs read the same collection; workflow status transitions (`draft → pending_approval → approved → paid`, or `→ rejected`) are **manual**, triggered via `PATCH /api/erp/records/{id}/status` from the Mock ERP UI's action buttons.
- Refresh model: page load / batch, not real-time push.

---

## 🗄️ Data Model
## 🗄️ Data Model (concrete)

Replaces the placeholder note *"carried over unchanged from the previous pass"* in the original README — that pass doesn't exist in this repo, so here are the actual schemas. MongoDB collections are shown as representative documents (not a rigid DDL — Mongo is schemaless, this is the contract the app code enforces via Pydantic). The one relational piece (`document_embeddings`, for pgvector) is shown as SQL.

Encrypted fields (AES-256-GCM, field-level, per [Auth & Security](#-auth--security)) are marked `🔒`.

---

### `users`
```json
{
  "_id": "ObjectId",
  "email": "string, unique, indexed",
  "password_hash": "string (bcrypt)",
  "full_name": "string",
  "role": "admin | analyst | viewer",
  "is_active": "boolean, default true",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
Index: `{email: 1}` unique.

---

### `refresh_tokens`
```json
{
  "_id": "ObjectId",
  "token_hash": "string, indexed",
  "user_id": "ObjectId, ref users._id",
  "expires_at": "datetime",
  "revoked": "boolean, default false",
  "created_at": "datetime"
}
```
Index: `{token_hash: 1}` unique, `{user_id: 1}`. TTL index on `expires_at` optional (or a scheduled cleanup — MVP can skip and just filter on read).

---

### `documents`
```json
{
  "_id": "ObjectId",
  "filename": "string (stored filename, e.g. {document_id}.enc)",
  "original_filename": "string",
  "mime_type": "application/pdf | application/vnd.openxmlformats-officedocument.wordprocessingml.document | image/png | image/jpeg",
  "file_size_bytes": "number",
  "storage_path": "string (backend/storage/uploads/{document_id}.enc)",
  "status": "uploaded | preprocessing | classifying | extracting | insight_pending | completed | failed | human_review",
  "classification": {
    "document_type": "one of the 14 classes | null",
    "decision": "AUTO_ACCEPT | REVIEW_LLM_FALLBACK | HUMAN_REVIEW | null",
    "confidence": "number 0-1 | null",
    "top_k": ["string"],
    "probabilities": { "<CLASS_NAME>": "number" },
    "model_version": "string",
    "source": "rule | ml | llm | llm_fallback"
  },
  "pii_redaction_map_ref": "🔒 string (encrypted token→real-value mapping, JSON blob)",
  "uploaded_by": "ObjectId, ref users._id",
  "error": {
    "code": "string | null",
    "message": "string | null",
    "stage": "ocr | classification | extraction | insight | null"
  },
  "retry_count": "number, default 0",
  "is_deleted": "boolean, default false",
  "deleted_at": "datetime | null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
Indexes: `{status: 1}`, `{classification.document_type: 1}`, `{uploaded_by: 1}`, `{created_at: -1}`.

---

### `extracted_documents`
```json
{
  "_id": "ObjectId",
  "document_id": "ObjectId, ref documents._id, unique",
  "document_type": "one of the 14 classes",
  "fields": "🔒 object — shape matches the corresponding <type>_extraction.txt JSON schema (e.g. business_invoice's invoice_number/vendor/line_items/... )",
  "field_confidences": { "<field_name>": "number 0-1" },
  "needs_review": "boolean",
  "extraction_source": "rule | llm | hybrid",
  "reviewed_by": "ObjectId, ref users._id | null",
  "reviewed_at": "datetime | null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
Index: `{document_id: 1}` unique, `{document_type: 1}`, `{needs_review: 1}`.

Note: only `fields` (the sensitive payload) is encrypted — `document_type`, `needs_review`, timestamps stay plaintext for queryability, matching the README's stated at-rest policy.

---

### `insights`
```json
{
  "_id": "ObjectId",
  "type": "risk | anomaly | trend | recommendation",
  "severity": "low | medium | high | critical",
  "title": "string, under 80 chars",
  "description": "string",
  "related_entity": "string (vendor/customer/lead name)",
  "related_document_ids": ["ObjectId, ref documents._id"],
  "status": "open | acknowledged | resolved",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
Indexes: `{status: 1, severity: 1}`, `{related_entity: 1}`, `{type: 1}`, `{created_at: -1}`.

---

### `erp_records`
```json
{
  "_id": "ObjectId",
  "record_type": "one of the 14 classes",
  "source": "seed | pipeline",
  "linked_document_id": "ObjectId, ref documents._id | null (null when source=seed)",
  "party_name": "string",
  "amount": "number | null",
  "currency": "string | null",
  "key_dates": { "issue_date": "date | null", "due_date": "date | null" },
  "erp_status": "draft | pending_approval | approved | paid | rejected",
  "status_history": [
    { "status": "string", "changed_by": "ObjectId, ref users._id", "changed_at": "datetime" }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
Indexes: `{record_type: 1, erp_status: 1}`, `{source: 1}`, `{party_name: 1}`.

---

### `chat_sessions`
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId, ref users._id",
  "messages": [
    {
      "role": "user | assistant",
      "content": "string",
      "source_document_ids": ["ObjectId, ref documents._id"],
      "retrieval_method": "semantic | keyword | hybrid | null",
      "created_at": "datetime"
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
Index: `{user_id: 1, updated_at: -1}`.

---

### `audit_logs`
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId, ref users._id | null (null for system-initiated actions)",
  "action": "upload | edit | erp_write | delete | login | logout | register",
  "resource_type": "document | extracted_document | erp_record | insight | user",
  "resource_id": "ObjectId",
  "detail": "object | null (e.g. field-level diff for edit actions)",
  "ip_address": "string | null",
  "created_at": "datetime"
}
```
Index: `{resource_type: 1, resource_id: 1}`, `{user_id: 1, created_at: -1}`.

---

### `document_embeddings` (PostgreSQL + pgvector)
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_embeddings (
    id           BIGSERIAL PRIMARY KEY,
    document_id  VARCHAR(24) NOT NULL,      -- Mongo ObjectId as string, ref documents._id
    chunk_index  INT NOT NULL,
    chunk_text   TEXT NOT NULL,             -- de-identified (PII already redacted before chunking)
    embedding    VECTOR(384) NOT NULL,      -- sentence-transformers/all-MiniLM-L6-v2
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX document_embeddings_document_id_idx ON document_embeddings (document_id);
CREATE INDEX document_embeddings_embedding_idx ON document_embeddings
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```
Chunking (MVP default): split `extracted_documents`-adjacent OCR/text by ~500-token windows with ~50-token overlap, one row per chunk. Upgrade path to `BAAI/bge-base-en-v1.5` means changing `VECTOR(384)` → `VECTOR(768)` and re-embedding all rows.

---

### Cross-collection relationships
```
users ──< refresh_tokens
users ──< documents (uploaded_by)
documents ──< extracted_documents (1:1, document_id)
documents ──< erp_records (linked_document_id, only when source=pipeline)
documents ──< insights (related_document_ids, many:many)
documents ──< document_embeddings (document_id, 1:many, Postgres)
users ──< chat_sessions
*  ──< audit_logs (resource_type + resource_id, polymorphic)
```

## 🔄 Final End-to-End Flow

1. **Upload** — `POST /api/documents/upload`; file AES-256-GCM encrypted and written to `UPLOAD_DIR`; `documents` record created (`status: uploaded`); logged to `audit_logs`.
2. **Preprocessing & OCR** — file decrypted in-memory only; routed by format; layout cached.
3. **Classification** — parallel rule/ML/LLM classifiers; confidence-routed; ties (<2% margin) forced to `REVIEW_LLM_FALLBACK`.
4. **PII Redaction** — sensitive fields masked before any LLM call; mapping stored encrypted.
5. **Specialized Extraction** — per-type agent runs its prompt template (above) on redacted text; rule-based value wins on field overlap; schema-validated; `needs_review` set per confidence threshold; failed calls retried per [Error Handling](#-error-handling--retry-policy).
6. **ERP Append** — written to `erp_records` (`source: pipeline`, `erp_status: draft`).
7. **Insight Generation** — LLM-judged Insight Agent runs immediately post-extraction (see [Insight Agent](#-insight-agent-llm-judged-risk--anomaly-detection)); non-blocking on failure.
8. **Embedding & Indexing** — de-identified text chunked/embedded into `document_embeddings`.
9. **Dashboard Read** — `GET /api/dashboard/kpis`, `/api/insights`, `/api/documents` on page load.
10. **Mock ERP Read & Manual Workflow** — `GET /api/erp/records`; status transitions via `PATCH .../status`, manual only.
11. **Chatbot Query** — `POST /api/chat/sessions/{id}/messages`; hybrid retrieval, RBAC-filtered, source-grounded.
12. **Audit Trail** — every write above logged to `audit_logs`.

---

## 🧪 Testing & CI (Roadmap — not built in this pass)

- Backend/ML: `pytest`, unit tests per agent + integration test for the full pipeline against fixture documents.
- Frontend: Jest + React Testing Library for both `frontend/` and `mock-erp-frontend/`.
- CI: GitHub Actions running lint + tests on PR (not yet configured).
- This is intentionally deferred until the core pipeline and both UIs are functionally complete.

---

## 🗺️ Roadmap

- [ ] Document upload & storage module (local disk, encrypted)
- [ ] OCR integration (PyMuPDF, python-docx, PaddleOCR)
- [ ] Layout feature extraction & caching
- [ ] Rule-based classification engine
- [ ] ML classification model (soft voting ensemble)
- [ ] LLM classifier (parallel evaluation) + tie-margin handling
- [ ] Confidence-based decision routing
- [ ] Specialized agents (all 14 types) using prompt templates above
- [ ] Insight generation agent (LLM-judged risk/anomaly/trend/recommendation)
- [ ] Dashboard UI (all pages listed in [Frontend Architecture](#-frontend-architecture))
- [ ] Document embedding pipeline (pgvector integration)
- [ ] Hybrid retrieval & ranking for RAG chatbot
- [ ] RAG chatbot UI
- [ ] Shared MongoDB schema (pipeline output + ERP data)
- [ ] Mock ERP workflow status transition UI
- [ ] Mock ERP data generation/seed scripts + `/api/erp/seed`
- [ ] Mock ERP backend API + UI
- [ ] Authentication (JWT access/refresh) & RBAC middleware
- [ ] Field-level + file-level AES-256-GCM encryption
- [ ] Error handling & retry logic across all pipeline stages
- [ ] Testing suite (pytest + Jest) — see [Testing & CI](#-testing--ci-roadmap--not-built-in-this-pass)
- [ ] CI pipeline (GitHub Actions)
- [ ] Containerized deployment (Docker Compose, then K8s) — deferred past MVP
- [ ] Swap local disk storage for S3-compatible storage (interface already abstracted)
- [ ] Swap env-var master key for real KMS (AWS/GCP)
- [ ] MFA / OAuth2 SSO — deferred past MVP
- [ ] ERP integration connectors (real external ERP systems)

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request for any feature requests, bug fixes, or improvements.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 📬 Contact

For questions or collaboration inquiries, please open an issue in this repository.
