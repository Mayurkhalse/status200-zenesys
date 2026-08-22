from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class StatusHistoryItem(BaseModel):
    status: str
    changed_by: str
    changed_at: datetime

class KeyDates(BaseModel):
    issue_date: Optional[str] = None
    due_date: Optional[str] = None

class ErpRecordItem(BaseModel):
    id: str
    record_type: str
    source: str  # seed | pipeline
    linked_document_id: Optional[str] = None
    party_name: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    key_dates: KeyDates
    erp_status: str  # draft | pending_approval | approved | paid | rejected
    status_history: List[StatusHistoryItem] = []
    created_at: datetime
    updated_at: datetime

class ErpRecordListResponse(BaseModel):
    items: List[ErpRecordItem]
    total: int

class UpdateErpStatusRequest(BaseModel):
    new_status: str  # pending_approval | approved | paid | rejected

class SeedErpRequest(BaseModel):
    count_per_type: int = 5
