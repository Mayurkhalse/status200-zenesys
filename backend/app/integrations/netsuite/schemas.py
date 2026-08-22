from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class NetSuiteSyncRequest(BaseModel):
    document_id: str = Field(..., description="ID of extracted document to sync with NetSuite")
    override_record_type: Optional[str] = Field(None, description="Optional override NetSuite record type")

class NetSuiteSyncResponse(BaseModel):
    success: bool
    document_id: str
    netsuite_record_type: str
    netsuite_internal_id: str
    netsuite_tran_id: Optional[str] = None
    synced_at: datetime
    message: str
    raw_payload: Optional[Dict[str, Any]] = None

class NetSuiteConnectionStatus(BaseModel):
    connected: bool
    account_id: str
    auth_method: str = "Token-Based Authentication (TBA / OAuth 1.0a)"
    mode: str
    message: str

class NetSuiteWebhookPayload(BaseModel):
    event_type: str = Field(..., description="SuiteScript event type e.g. record.created, record.updated")
    record_type: str = Field(..., description="NetSuite record type e.g. vendorBill, purchaseOrder")
    internal_id: str = Field(..., description="NetSuite record internal ID")
    tran_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
