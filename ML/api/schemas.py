"""
Pydantic API Schemas for ERP Document Classifier Service.
"""
from pydantic import BaseModel
from typing import Dict, List

class ClassificationRequest(BaseModel):
    file_path: str

class ClassificationResponse(BaseModel):
    document_type: str
    confidence: float
    decision: str
    top_k: List[str]
    probabilities: Dict[str, float]
    model_version: str
