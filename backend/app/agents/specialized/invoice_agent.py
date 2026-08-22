from typing import Dict, Any, Tuple
from app.agents.base.base_agent import BaseAgent

class InvoiceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent_invoice_01",
            agent_name="Business Invoice Extraction Agent",
            document_type="BUSINESS_INVOICE",
            prompt_filename="business_invoice_extraction.txt",
            version="1.1.0"
        )

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        errors = []
        if not data.get("invoice_number"):
            errors.append("Missing required field 'invoice_number'")
        if not data.get("vendor"):
            errors.append("Missing required field 'vendor'")
        if data.get("total") is None and data.get("subtotal") is None:
            errors.append("Missing invoice financial total or subtotal")

        # Sanity check line items math
        line_items = data.get("line_items", [])
        if isinstance(line_items, list) and len(line_items) > 0:
            calc_total = 0.0
            for item in line_items:
                if isinstance(item, dict) and "amount" in item and item["amount"]:
                    calc_total += float(item["amount"])
            total_val = data.get("total") or data.get("subtotal")
            if total_val and calc_total > 0 and abs(calc_total - float(total_val)) > (0.1 * float(total_val)):
                errors.append(f"Line items total ({calc_total}) mismatches invoice total ({total_val})")

        return len(errors) == 0, errors
