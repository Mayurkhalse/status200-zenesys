from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from bson import ObjectId
from app.db.database import get_mongo_db
from app.core.rbac import get_current_user, require_roles, UserSession
from app.models.schemas.insights import InsightItem, InsightListResponse, UpdateInsightRequest
from app.services.audit_service import audit_service

router = APIRouter(prefix="/insights", tags=["Insights"])

@router.get("", response_model=InsightListResponse)
async def list_insights(
    type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    related_document_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserSession = Depends(get_current_user)
):
    db = get_mongo_db()
    query = {}
    if type:
        query["type"] = type
    if severity:
        query["severity"] = severity
    if status:
        query["status"] = status
    if related_document_id:
        query["related_document_ids"] = ObjectId(related_document_id)

    total = await db.insights.count_documents(query)
    cursor = db.insights.find(query).sort("created_at", -1).skip((page - 1) * limit).limit(limit)

    items = []
    async for ins in cursor:
        items.append(InsightItem(
            id=str(ins["_id"]),
            type=ins["type"],
            severity=ins["severity"],
            title=ins["title"],
            description=ins["description"],
            related_entity=ins["related_entity"],
            related_document_ids=[str(d) for d in ins.get("related_document_ids", [])],
            status=ins["status"],
            created_at=ins["created_at"],
            updated_at=ins["updated_at"]
        ))

    return InsightListResponse(items=items, total=total)

@router.patch("/{insight_id}", response_model=InsightItem)
async def update_insight_status(
    insight_id: str,
    req: UpdateInsightRequest,
    current_user: UserSession = Depends(require_roles(["admin", "analyst"]))
):
    db = get_mongo_db()
    ins_oid = ObjectId(insight_id)
    ins = await db.insights.find_one({"_id": ins_oid})
    if not ins:
        raise HTTPException(status_code=404, detail="Insight not found")

    now = datetime.now(timezone.utc)
    await db.insights.update_one(
        {"_id": ins_oid},
        {"$set": {"status": req.status, "updated_at": now}}
    )

    await audit_service.log_action(current_user.user_id, "edit", "insight", insight_id, detail={"status": req.status})

    updated = await db.insights.find_one({"_id": ins_oid})
    return InsightItem(
        id=str(updated["_id"]),
        type=updated["type"],
        severity=updated["severity"],
        title=updated["title"],
        description=updated["description"],
        related_entity=updated["related_entity"],
        related_document_ids=[str(d) for d in updated.get("related_document_ids", [])],
        status=updated["status"],
        created_at=updated["created_at"],
        updated_at=updated["updated_at"]
    )
