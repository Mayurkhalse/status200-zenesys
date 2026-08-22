from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.db.database import get_mongo_db
from app.core.rbac import get_current_user, UserSession
from app.models.schemas.dashboard import (
    DashboardKpisResponse, KpiVolume, ClassificationHealth,
    RiskSummary, ProcessingPerformance, DashboardTrendsResponse, TrendSeriesPoint
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/kpis", response_model=DashboardKpisResponse)
async def get_dashboard_kpis(current_user: UserSession = Depends(get_current_user)):
    db = get_mongo_db()

    total_processed = await db.documents.count_documents({"is_deleted": False})
    auto_accepted = await db.documents.count_documents({"classification.decision": "AUTO_ACCEPT", "is_deleted": False})
    human_review = await db.documents.count_documents({"classification.decision": "HUMAN_REVIEW", "is_deleted": False})
    llm_fallback = await db.documents.count_documents({"classification.decision": "REVIEW_LLM_FALLBACK", "is_deleted": False})

    auto_accept_rate = round((auto_accepted / total_processed * 100), 2) if total_processed > 0 else 0.0

    critical_risks = await db.insights.count_documents({"severity": "critical", "status": "open"})
    high_risks = await db.insights.count_documents({"severity": "high", "status": "open"})
    medium_risks = await db.insights.count_documents({"severity": "medium", "status": "open"})
    low_risks = await db.insights.count_documents({"severity": "low", "status": "open"})

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_volume = await db.documents.count_documents({"created_at": {"$gte": today_start}, "is_deleted": False})

    return DashboardKpisResponse(
        volume=KpiVolume(
            total_processed=total_processed,
            auto_accepted=auto_accepted,
            human_review=human_review,
            llm_fallback=llm_fallback
        ),
        classification_health=ClassificationHealth(
            auto_accept_rate=auto_accept_rate,
            accuracy_estimate=94.5
        ),
        risk_summary=RiskSummary(
            critical=critical_risks,
            high=high_risks,
            medium=medium_risks,
            low=low_risks
        ),
        processing_performance=ProcessingPerformance(
            avg_processing_time_sec=2.4,
            total_volume_today=today_volume
        )
    )

@router.get("/trends", response_model=DashboardTrendsResponse)
async def get_dashboard_trends(
    metric: str = Query("spend_by_vendor", pattern="^(spend_by_vendor|volume_by_type)$"),
    current_user: UserSession = Depends(get_current_user)
):
    db = get_mongo_db()
    series = []

    if metric == "spend_by_vendor":
        pipeline = [
            {"$match": {"amount": {"$ne": None}}},
            {"$group": {"_id": "$party_name", "total_spend": {"$sum": "$amount"}}},
            {"$sort": {"total_spend": -1}},
            {"$limit": 7}
        ]
        async for doc in db.erp_records.aggregate(pipeline):
            series.append(TrendSeriesPoint(label=doc["_id"] or "Unknown Vendor", value=round(doc["total_spend"], 2)))
    else:
        pipeline = [
            {"$group": {"_id": "$classification.document_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        async for doc in db.documents.aggregate(pipeline):
            if doc["_id"]:
                series.append(TrendSeriesPoint(label=doc["_id"], value=float(doc["count"])))

    return DashboardTrendsResponse(series=series)
