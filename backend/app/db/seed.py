import asyncio
from datetime import datetime, timezone
from app.db.database import get_mongo_db, init_db
from app.core.security import get_password_hash

async def seed_data():
    await init_db()
    db = get_mongo_db()

    # Seed Admin User
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

    # Seed Mock ERP Baseline Records
    existing_erp = await db.erp_records.count_documents({})
    if existing_erp == 0:
        vendors = ["Acme Corp", "Global Logistics LLC", "Apex Supplies", "TechNova Solutions", "Starlight Systems"]
        types = ["BUSINESS_INVOICE", "PURCHASE_ORDER", "SALES_ORDER", "LEAD", "QUOTATION"]
        statuses = ["draft", "pending_approval", "approved", "paid"]
        
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

if __name__ == "__main__":
    asyncio.run(seed_data())
