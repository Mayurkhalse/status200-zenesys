from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime, timezone
from bson import ObjectId

from app.db.database import get_mongo_db
from app.core.rbac import get_current_user, UserSession
from app.integrations.netsuite.schemas import (
    NetSuiteConnectionStatus, NetSuiteSyncRequest, NetSuiteSyncResponse
)
from app.integrations.netsuite.netsuite_client import netsuite_client

router = APIRouter(prefix="/netsuite", tags=["NetSuite ERP Integration"])

@router.get("/status", response_model=NetSuiteConnectionStatus)
async def check_netsuite_status(current_user: UserSession = Depends(get_current_user)):
    """Verifies NetSuite SuiteTalk REST API connection status and Token-Based Auth (TBA)."""
    connected, msg = await netsuite_client.test_connection()
    return NetSuiteConnectionStatus(
        connected=connected,
        account_id=netsuite_client.account_id,
        auth_method="Token-Based Authentication (TBA / OAuth 1.0a)",
        mode="Live SuiteTalk REST API" if "placeholder" not in netsuite_client.consumer_key else "Simulated Sandbox Mode",
        message=msg
    )

@router.post("/sync/document/{document_id}", response_model=NetSuiteSyncResponse)
async def sync_document_to_netsuite(
    document_id: str,
    current_user: UserSession = Depends(get_current_user)
):
    """Pushes extracted document fields into Oracle NetSuite ERP record."""
    db = get_mongo_db()
    doc_oid = ObjectId(document_id) if ObjectId.is_valid(document_id) else document_id

    # Fetch document and extracted fields
    doc = await db.documents.find_one({"_id": doc_oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    ext_doc = await db.extracted_documents.find_one({"document_id": doc_oid})
    fields = ext_doc.get("fields", {}) if ext_doc else {}
    doc_type = doc.get("classification", {}).get("document_type", "OTHER")

    # Invoke NetSuite Client
    sync_res = await netsuite_client.sync_record(doc_type, fields)

    now = datetime.now(timezone.utc)

    # Store NetSuite Sync Record in MongoDB
    netsuite_audit = {
        "document_id": doc_oid,
        "netsuite_record_type": sync_res["netsuite_record_type"],
        "netsuite_internal_id": sync_res["netsuite_internal_id"],
        "netsuite_tran_id": sync_res["netsuite_tran_id"],
        "synced_by": ObjectId(current_user.user_id) if ObjectId.is_valid(current_user.user_id) else current_user.user_id,
        "synced_at": now,
        "raw_payload": sync_res["raw_payload"]
    }
    await db.netsuite_sync_logs.insert_one(netsuite_audit)

    # Update document with NetSuite Sync reference
    await db.documents.update_one(
        {"_id": doc_oid},
        {"$set": {
            "netsuite_sync": {
                "synced": True,
                "record_type": sync_res["netsuite_record_type"],
                "internal_id": sync_res["netsuite_internal_id"],
                "synced_at": now
            }
        }}
    )

    return NetSuiteSyncResponse(
        success=sync_res["success"],
        document_id=document_id,
        netsuite_record_type=sync_res["netsuite_record_type"],
        netsuite_internal_id=sync_res["netsuite_internal_id"],
        netsuite_tran_id=sync_res["netsuite_tran_id"],
        synced_at=now,
        message=sync_res["message"],
        raw_payload=sync_res["raw_payload"]
    )
