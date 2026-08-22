import random
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from bson import ObjectId

from app.db.database import get_mongo_db
from app.core.rbac import get_current_user, get_current_user_optional, require_roles, UserSession
from app.models.schemas.erp import (
    ErpRecordItem, ErpRecordListResponse, KeyDates,
    StatusHistoryItem, UpdateErpStatusRequest, SeedErpRequest
)
from app.services.audit_service import audit_service

router = APIRouter(prefix="/erp", tags=["Mock ERP"])

@router.get("/records", response_model=ErpRecordListResponse)
async def list_erp_records(
    record_type: Optional[str] = None,
    erp_status: Optional[str] = None,
    source: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserSession = Depends(get_current_user_optional)
):
    db = get_mongo_db()
    query = {}
    if record_type:
        query["record_type"] = record_type
    if erp_status:
        query["erp_status"] = erp_status
    if source:
        query["source"] = source

    total = await db.erp_records.count_documents(query)
    cursor = db.erp_records.find(query).sort("created_at", -1).skip((page - 1) * limit).limit(limit)

    items = []
    async for rec in cursor:
        items.append(ErpRecordItem(
            id=str(rec["_id"]),
            record_type=rec["record_type"],
            source=rec["source"],
            linked_document_id=str(rec["linked_document_id"]) if rec.get("linked_document_id") else None,
            party_name=rec["party_name"],
            amount=rec.get("amount"),
            currency=rec.get("currency", "USD"),
            key_dates=KeyDates(
                issue_date=rec.get("key_dates", {}).get("issue_date"),
                due_date=rec.get("key_dates", {}).get("due_date")
            ),
            erp_status=rec["erp_status"],
            status_history=[
                StatusHistoryItem(
                    status=s["status"],
                    changed_by=str(s["changed_by"]),
                    changed_at=s["changed_at"]
                ) for s in rec.get("status_history", [])
            ],
            created_at=rec["created_at"],
            updated_at=rec["updated_at"]
        ))

    return ErpRecordListResponse(items=items, total=total)

@router.get("/records/{record_id}", response_model=ErpRecordItem)
async def get_erp_record(record_id: str, current_user: UserSession = Depends(get_current_user_optional)):
    db = get_mongo_db()
    rec = await db.erp_records.find_one({"_id": ObjectId(record_id)})
    if not rec:
        raise HTTPException(status_code=404, detail="ERP record not found")

    return ErpRecordItem(
        id=str(rec["_id"]),
        record_type=rec["record_type"],
        source=rec["source"],
        linked_document_id=str(rec["linked_document_id"]) if rec.get("linked_document_id") else None,
        party_name=rec["party_name"],
        amount=rec.get("amount"),
        currency=rec.get("currency", "USD"),
        key_dates=KeyDates(
            issue_date=rec.get("key_dates", {}).get("issue_date"),
            due_date=rec.get("key_dates", {}).get("due_date")
        ),
        erp_status=rec["erp_status"],
        status_history=[
            StatusHistoryItem(
                status=s["status"],
                changed_by=str(s["changed_by"]),
                changed_at=s["changed_at"]
            ) for s in rec.get("status_history", [])
        ],
        created_at=rec["created_at"],
        updated_at=rec["updated_at"]
    )

@router.patch("/records/{record_id}/status", response_model=ErpRecordItem)
async def update_erp_record_status(
    record_id: str,
    req: UpdateErpStatusRequest,
    current_user: UserSession = Depends(get_current_user_optional)
):
    db = get_mongo_db()
    rec_oid = ObjectId(record_id)
    rec = await db.erp_records.find_one({"_id": rec_oid})
    if not rec:
        raise HTTPException(status_code=404, detail="ERP record not found")

    now = datetime.now(timezone.utc)
    user_id_val = ObjectId(current_user.user_id) if ObjectId.is_valid(current_user.user_id) else current_user.user_id
    new_history_entry = {
        "status": req.new_status,
        "changed_by": user_id_val,
        "changed_at": now
    }

    await db.erp_records.update_one(
        {"_id": rec_oid},
        {
            "$set": {"erp_status": req.new_status, "updated_at": now},
            "$push": {"status_history": new_history_entry}
        }
    )

    await audit_service.log_action(current_user.user_id, "erp_write", "erp_record", record_id, detail={"new_status": req.new_status})

    updated = await db.erp_records.find_one({"_id": rec_oid})
    return ErpRecordItem(
        id=str(updated["_id"]),
        record_type=updated["record_type"],
        source=updated["source"],
        linked_document_id=str(updated["linked_document_id"]) if updated.get("linked_document_id") else None,
        party_name=updated["party_name"],
        amount=updated.get("amount"),
        currency=updated.get("currency", "USD"),
        key_dates=KeyDates(
            issue_date=updated.get("key_dates", {}).get("issue_date"),
            due_date=updated.get("key_dates", {}).get("due_date")
        ),
        erp_status=updated["erp_status"],
        status_history=[
            StatusHistoryItem(
                status=s["status"],
                changed_by=str(s["changed_by"]),
                changed_at=s["changed_at"]
            ) for s in updated.get("status_history", [])
        ],
        created_at=updated["created_at"],
        updated_at=updated["updated_at"]
    )

@router.post("/seed")
async def seed_erp_data(req: SeedErpRequest, current_user: UserSession = Depends(get_current_user_optional)):
    db = get_mongo_db()
    vendors = ["Acme Corp", "Global Logistics LLC", "Apex Supplies", "TechNova Solutions", "Starlight Systems"]
    types = ["BUSINESS_INVOICE", "PURCHASE_ORDER", "SALES_ORDER", "LEAD", "QUOTATION"]
    statuses = ["draft", "pending_approval", "approved", "paid"]

    seeded_count = 0
    now = datetime.now(timezone.utc)
    user_id_val = ObjectId(current_user.user_id) if (hasattr(current_user, "user_id") and ObjectId.is_valid(current_user.user_id)) else "000000000000000000000000"

    for doc_type in types:
        for _ in range(req.count_per_type):
            vendor = random.choice(vendors)
            amount = round(random.uniform(500, 15000), 2)
            issue_date = (now - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            due_date = (now + timedelta(days=random.randint(5, 45))).strftime("%Y-%m-%d")
            st = random.choice(statuses)

            doc = {
                "record_type": doc_type,
                "source": "seed",
                "linked_document_id": None,
                "party_name": vendor,
                "amount": amount,
                "currency": "USD",
                "key_dates": {"issue_date": issue_date, "due_date": due_date},
                "erp_status": st,
                "status_history": [{
                    "status": st,
                    "changed_by": user_id_val,
                    "changed_at": now
                }],
                "created_at": now,
                "updated_at": now
            }
            await db.erp_records.insert_one(doc)
            seeded_count += 1

    return {"seeded": seeded_count}
