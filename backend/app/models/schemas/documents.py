from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ClassificationInfo(BaseModel):
    document_type: Optional[str] = None
    decision: Optional[str] = None
    confidence: Optional[float] = None
    top_k: Optional[List[str]] = []
    probabilities: Optional[Dict[str, float]] = {}
    model_version: Optional[str] = "1.0.0"
    source: Optional[str] = "rule"

class ErrorDetail(BaseModel):
    code: Optional[str] = None
    message: Optional[str] = None
    stage: Optional[str] = None

class DocumentItem(BaseModel):
    document_id: str
    filename: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    status: str
    classification: Optional[ClassificationInfo] = None
    uploaded_by: str
    error: Optional[ErrorDetail] = None
    created_at: datetime
    updated_at: datetime

class DocumentListResponse(BaseModel):
    items: List[DocumentItem]
    total: int
    page: int
    limit: int

class DocumentStatusResponse(BaseModel):
    status: str
    decision: Optional[str] = None
    error: Optional[ErrorDetail] = None
