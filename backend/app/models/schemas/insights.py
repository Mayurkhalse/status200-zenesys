from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class InsightItem(BaseModel):
    id: str
    type: str  # risk | anomaly | trend | recommendation
    severity: str  # low | medium | high | critical
    title: str
    description: str
    related_entity: str
    related_document_ids: List[str] = []
    status: str  # open | acknowledged | resolved
    created_at: datetime
    updated_at: datetime

class InsightListResponse(BaseModel):
    items: List[InsightItem]
    total: int

class UpdateInsightRequest(BaseModel):
    status: str  # acknowledged | resolved
