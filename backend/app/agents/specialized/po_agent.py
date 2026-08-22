from typing import Dict, Any, Tuple
from app.agents.base.base_agent import BaseAgent

class PurchaseOrderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent_po_02",
            agent_name="Purchase Order Extraction Agent",
            document_type="PURCHASE_ORDER",
            prompt_filename="purchase_order_extraction.txt",
            version="1.1.0"
        )

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        errors = []
        if not data.get("po_number"):
            errors.append("Missing required field 'po_number'")
        if not data.get("buyer") and not data.get("vendor"):
            errors.append("Missing buyer or vendor details")
        return len(errors) == 0, errors

class SalesOrderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent_sales_03",
            agent_name="Sales Order Extraction Agent",
            document_type="SALES_ORDER",
            prompt_filename="sales_order_extraction.txt",
            version="1.1.0"
        )

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        errors = []
        if not data.get("so_number") and not data.get("order_number"):
            errors.append("Missing sales order identification number")
        if not data.get("customer"):
            errors.append("Missing customer details")
        return len(errors) == 0, errors
