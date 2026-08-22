from typing import Dict, Any, Tuple
from app.agents.base.base_agent import BaseAgent

class QuotationAgent(BaseAgent):
    def __init__(self):
        super().__init__("agent_quote_06", "Quotation Agent", "QUOTATION", "quotation_extraction.txt")

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        return True, []

class ProposalAgent(BaseAgent):
    def __init__(self):
        super().__init__("agent_prop_07", "Proposal Agent", "PROPOSAL", "proposal_extraction.txt")

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        return True, []

class ReceiptAgent(BaseAgent):
    def __init__(self):
        super().__init__("agent_rcpt_08", "Receipt Agent", "RECEIPT", "receipt_extraction.txt")

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        return True, []

class DeliveryNoteAgent(BaseAgent):
    def __init__(self):
        super().__init__("agent_deliv_09", "Delivery Note Agent", "DELIVERY_NOTE", "delivery_note_extraction.txt")

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        return True, []

class NoteAgent(BaseAgent):
    def __init__(self, doc_type: str = "CREDIT_NOTE"):
        super().__init__("agent_note_10", f"{doc_type} Agent", doc_type, "credit_note_extraction.txt" if doc_type == "CREDIT_NOTE" else "debit_note_extraction.txt")

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        return True, []

class RFQAgent(BaseAgent):
    def __init__(self):
        super().__init__("agent_rfq_11", "RFQ Agent", "RFQ", "rfq_extraction.txt")

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        return True, []

class GenericDocumentAgent(BaseAgent):
    def __init__(self):
        super().__init__("agent_gen_12", "Generic Document Agent", "OTHER", "other_extraction.txt")

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        return True, []
