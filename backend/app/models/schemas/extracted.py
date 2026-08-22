from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# 1. Business Invoice
class InvoiceLineItem(BaseModel):
    description: str
    qty: float
    unit_price: float
    amount: float

class BusinessInvoiceSchema(BaseModel):
    invoice_number: Optional[str] = None
    vendor: Optional[str] = None
    bill_to: Optional[str] = None
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    line_items: List[InvoiceLineItem] = []
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    currency: Optional[str] = None
    payment_terms: Optional[str] = None

# 2. Purchase Order
class PurchaseOrderSchema(BaseModel):
    po_number: Optional[str] = None
    vendor: Optional[str] = None
    buyer: Optional[str] = None
    order_date: Optional[str] = None
    delivery_date: Optional[str] = None
    line_items: List[InvoiceLineItem] = []
    total: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None

# 3. Sales Order
class SalesOrderSchema(BaseModel):
    so_number: Optional[str] = None
    customer: Optional[str] = None
    salesperson: Optional[str] = None
    order_date: Optional[str] = None
    expected_shipment_date: Optional[str] = None
    line_items: List[InvoiceLineItem] = []
    total: Optional[float] = None
    currency: Optional[str] = None

# 4. Quotation
class QuotationSchema(BaseModel):
    quote_number: Optional[str] = None
    client: Optional[str] = None
    issue_date: Optional[str] = None
    valid_until: Optional[str] = None
    line_items: List[InvoiceLineItem] = []
    total: Optional[float] = None
    currency: Optional[str] = None
    terms: Optional[str] = None

# 5. Proposal
class ProposalSchema(BaseModel):
    proposal_id: Optional[str] = None
    client: Optional[str] = None
    submitted_by: Optional[str] = None
    submission_date: Optional[str] = None
    scope_summary: Optional[str] = None
    estimated_value: Optional[float] = None
    validity_date: Optional[str] = None

# 6. Contract
class ContractClause(BaseModel):
    clause_type: str
    summary: str

class ContractSchema(BaseModel):
    contract_id: Optional[str] = None
    parties: List[str] = []
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    contract_value: Optional[float] = None
    key_clauses: List[ContractClause] = []
    renewal_terms: Optional[str] = None

# 7. Lead
class LeadSchema(BaseModel):
    lead_name: Optional[str] = None
    company: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    source: Optional[str] = None
    interest: Optional[str] = None
    status: Optional[str] = None

# 8. Receipt
class ReceiptSchema(BaseModel):
    receipt_number: Optional[str] = None
    merchant: Optional[str] = None
    transaction_date: Optional[str] = None
    line_items: List[InvoiceLineItem] = []
    total: Optional[float] = None
    payment_method: Optional[str] = None

# 9. Delivery Note
class DeliveryLineItem(BaseModel):
    description: str
    qty_shipped: float

class DeliveryNoteSchema(BaseModel):
    delivery_note_number: Optional[str] = None
    linked_po_number: Optional[str] = None
    vendor: Optional[str] = None
    delivery_date: Optional[str] = None
    line_items: List[DeliveryLineItem] = []
    received_by: Optional[str] = None

# 10. Credit Note
class CreditNoteSchema(BaseModel):
    credit_note_number: Optional[str] = None
    linked_invoice_number: Optional[str] = None
    vendor: Optional[str] = None
    issue_date: Optional[str] = None
    credit_amount: Optional[float] = None
    reason: Optional[str] = None

# 11. Debit Note
class DebitNoteSchema(BaseModel):
    debit_note_number: Optional[str] = None
    linked_invoice_number: Optional[str] = None
    vendor: Optional[str] = None
    issue_date: Optional[str] = None
    debit_amount: Optional[float] = None
    reason: Optional[str] = None

# 12. Payment Receipt
class PaymentReceiptSchema(BaseModel):
    receipt_number: Optional[str] = None
    linked_invoice_number: Optional[str] = None
    payer: Optional[str] = None
    payment_date: Optional[str] = None
    amount_paid: Optional[float] = None
    payment_method: Optional[str] = None
    remaining_balance: Optional[float] = None

# 13. RFQ
class RFQLineItem(BaseModel):
    description: str
    qty_requested: float

class RFQSchema(BaseModel):
    rfq_number: Optional[str] = None
    requester: Optional[str] = None
    issue_date: Optional[str] = None
    response_deadline: Optional[str] = None
    line_items: List[RFQLineItem] = []

# 14. Other
class OtherSchema(BaseModel):
    raw_text_summary: Optional[str] = None
    detected_keywords: List[str] = []

# Extracted Document API wrapper schemas
class ExtractedDocumentItem(BaseModel):
    id: str
    document_id: str
    document_type: str
    fields: Dict[str, Any]
    field_confidences: Dict[str, float]
    needs_review: bool
    extraction_source: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class UpdateExtractedDocumentRequest(BaseModel):
    fields: Dict[str, Any]
