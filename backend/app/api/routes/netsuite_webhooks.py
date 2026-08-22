from fastapi import APIRouter, HTTPException, Header, status
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.db.database import get_mongo_db
from app.integrations.netsuite.schemas import NetSuiteWebhookPayload

router = APIRouter(prefix="/netsuite/webhooks", tags=["NetSuite Webhooks"])

@router.post("/event")
async def handle_netsuite_webhook(
    payload: NetSuiteWebhookPayload,
    x_netsuite_signature: Optional[str] = Header(None)
):
    """Webhook listener for SuiteScript record creation/update events triggered inside NetSuite."""
    db = get_mongo_db()
    now = datetime.now(timezone.utc)

    event_record = {
        "event_type": payload.event_type,
        "record_type": payload.record_type,
        "internal_id": payload.internal_id,
        "tran_id": payload.tran_id,
        "data": payload.data,
        "signature_header": x_netsuite_signature,
        "received_at": now
    }

    await db.netsuite_webhooks.insert_one(event_record)

    # Automatically create/update master ERP ledger record
    if payload.tran_id:
        await db.erp_records.update_one(
            {"party_name": payload.internal_id},
            {
                "$set": {
                    "source": "netsuite_webhook",
                    "erp_status": "approved" if "created" in payload.event_type else "updated",
                    "updated_at": now
                }
            },
            upsert=True
        )

    return {
        "status": "processed",
        "event_type": payload.event_type,
        "internal_id": payload.internal_id,
        "timestamp": now
    }
