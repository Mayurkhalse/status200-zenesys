import asyncio
from datetime import datetime, timezone, timedelta
from app.db.database import get_mongo_db, init_db
from app.core.security import get_password_hash
from app.core.encryption import encryption_service

async def seed_data():
    await init_db()
    db = get_mongo_db()

    # 1. Seed Admin User
    admin_email = "admin@intelliparse.ai"
    existing_admin = await db.users.find_one({"email": admin_email})
    if not existing_admin:
        admin_doc = {
            "email": admin_email,
            "password_hash": get_password_hash("Admin@123"),
            "full_name": "Admin User",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        res = await db.users.insert_one(admin_doc)
        admin_id = res.inserted_id
        print(f"Created default admin user: {admin_email} / Admin@123")
    else:
        admin_id = existing_admin["_id"]
        print(f"Admin user already exists: {admin_email}")

    # 2. Seed Mock ERP Baseline Records
    existing_erp = await db.erp_records.count_documents({})
    if existing_erp == 0:
        sample_records = [
            {"record_type": "BUSINESS_INVOICE", "party_name": "Acme Corp", "amount": 12500.00, "erp_status": "approved"},
            {"record_type": "PURCHASE_ORDER", "party_name": "Global Logistics LLC", "amount": 8450.50, "erp_status": "pending_approval"},
            {"record_type": "SALES_ORDER", "party_name": "Apex Supplies", "amount": 3200.00, "erp_status": "paid"},
            {"record_type": "QUOTATION", "party_name": "TechNova Solutions", "amount": 15000.00, "erp_status": "draft"},
            {"record_type": "LEAD", "party_name": "Starlight Systems", "amount": 4500.00, "erp_status": "draft"}
        ]

        now = datetime.now(timezone.utc)
        for rec in sample_records:
            doc = {
                "record_type": rec["record_type"],
                "source": "seed",
                "linked_document_id": None,
                "party_name": rec["party_name"],
                "amount": rec["amount"],
                "currency": "USD",
                "key_dates": {"issue_date": "2026-08-01", "due_date": "2026-08-30"},
                "erp_status": rec["erp_status"],
                "status_history": [{
                    "status": rec["erp_status"],
                    "changed_by": admin_id,
                    "changed_at": now
                }],
                "created_at": now,
                "updated_at": now
            }
            await db.erp_records.insert_one(doc)
        print("Seeded 5 baseline Mock ERP records.")
    else:
        print(f"Mock ERP already has {existing_erp} records.")

    # 3. Seed Sample Documents & Extracted Documents
    existing_docs = await db.documents.count_documents({})
    if existing_docs == 0:
        now = datetime.now(timezone.utc)
        sample_docs = [
            {
                "original_filename": "invoice_acme_2026.pdf",
                "storage_path": "./storage/uploads/invoice_acme_2026.pdf",
                "file_hash": "hash_inv_01",
                "mime_type": "application/pdf",
                "file_size": 42150,
                "uploaded_by": admin_id,
                "status": "completed",
                "classification": {
                    "document_type": "BUSINESS_INVOICE",
                    "decision": "AUTO_ACCEPT",
                    "confidence": 0.94,
                    "top_k": ["BUSINESS_INVOICE", "RECEIPT"],
                    "source": "ml"
                },
                "created_at": now - timedelta(days=2),
                "updated_at": now - timedelta(days=2)
            },
            {
                "original_filename": "po_global_logistics.pdf",
                "storage_path": "./storage/uploads/po_global_logistics.pdf",
                "file_hash": "hash_po_02",
                "mime_type": "application/pdf",
                "file_size": 38900,
                "uploaded_by": admin_id,
                "status": "completed",
                "classification": {
                    "document_type": "PURCHASE_ORDER",
                    "decision": "AUTO_ACCEPT",
                    "confidence": 0.91,
                    "top_k": ["PURCHASE_ORDER", "SALES_ORDER"],
                    "source": "ml"
                },
                "created_at": now - timedelta(days=1),
                "updated_at": now - timedelta(days=1)
            },
            {
                "original_filename": "sales_order_apex.pdf",
                "storage_path": "./storage/uploads/sales_order_apex.pdf",
                "file_hash": "hash_so_03",
                "mime_type": "application/pdf",
                "file_size": 31200,
                "uploaded_by": admin_id,
                "status": "completed",
                "classification": {
                    "document_type": "SALES_ORDER",
                    "decision": "AUTO_ACCEPT",
                    "confidence": 0.89,
                    "top_k": ["SALES_ORDER", "QUOTATION"],
                    "source": "rule"
                },
                "created_at": now,
                "updated_at": now
            },
            {
                "original_filename": "quotation_technova.pdf",
                "storage_path": "./storage/uploads/quotation_technova.pdf",
                "file_hash": "hash_quote_04",
                "mime_type": "application/pdf",
                "file_size": 29800,
                "uploaded_by": admin_id,
                "status": "human_review",
                "classification": {
                    "document_type": "QUOTATION",
                    "decision": "REVIEW_LLM_FALLBACK",
                    "confidence": 0.72,
                    "top_k": ["QUOTATION", "PROPOSAL"],
                    "source": "ml"
                },
                "created_at": now,
                "updated_at": now
            },
            {
                "original_filename": "crm_lead_starlight.pdf",
                "storage_path": "./storage/uploads/crm_lead_starlight.pdf",
                "file_hash": "hash_lead_05",
                "mime_type": "application/pdf",
                "file_size": 24500,
                "uploaded_by": admin_id,
                "status": "completed",
                "classification": {
                    "document_type": "LEAD",
                    "decision": "AUTO_ACCEPT",
                    "confidence": 0.88,
                    "top_k": ["LEAD", "PROPOSAL"],
                    "source": "rule"
                },
                "created_at": now,
                "updated_at": now
            }
        ]

        for s_doc in sample_docs:
            d_res = await db.documents.insert_one(s_doc)
            doc_id = d_res.inserted_id

            # Create extracted document fields
            fields = {
                "vendor": s_doc["original_filename"].split("_")[1].capitalize(),
                "customer": "IntelliParse Client",
                "total": 12500.00 if "invoice" in s_doc["original_filename"] else 8450.50,
                "currency": "USD",
                "issue_date": "2026-08-01",
                "due_date": "2026-08-30"
            }
            enc_fields = encryption_service.encrypt_field(fields)

            ext_doc = {
                "document_id": doc_id,
                "document_type": s_doc["classification"]["document_type"],
                "fields": enc_fields,
                "field_confidences": {"total": 0.95, "vendor": 0.95},
                "needs_review": s_doc["status"] == "human_review",
                "extraction_source": s_doc["classification"]["source"],
                "created_at": s_doc["created_at"],
                "updated_at": s_doc["updated_at"]
            }
            await db.extracted_documents.insert_one(ext_doc)

            # Insert sample insight
            insight_doc = {
                "type": "risk" if s_doc["status"] == "human_review" else "trend",
                "severity": "high" if s_doc["status"] == "human_review" else "low",
                "title": f"Telemetry verified for {s_doc['classification']['document_type']}",
                "description": f"Extracted fields and classification health logged for {s_doc['original_filename']}.",
                "related_entity": fields["vendor"],
                "related_document_ids": [doc_id],
                "status": "open",
                "created_at": now,
                "updated_at": now
            }
            await db.insights.insert_one(insight_doc)

        print("Seeded 5 sample documents, extracted fields, and telemetry insights.")
    else:
        print(f"MongoDB already has {existing_docs} documents.")

if __name__ == "__main__":
    asyncio.run(seed_data())
