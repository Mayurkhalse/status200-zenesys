import os
from typing import Dict, Any, Tuple
from app.services.llm_service import llm_service

PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents", "specialized", "prompts")

PROMPT_FILE_MAP = {
    "BUSINESS_INVOICE": "business_invoice_extraction.txt",
    "PURCHASE_ORDER": "purchase_order_extraction.txt",
    "SALES_ORDER": "sales_order_extraction.txt",
    "QUOTATION": "quotation_extraction.txt",
    "PROPOSAL": "proposal_extraction.txt",
    "CONTRACT": "contract_extraction.txt",
    "LEAD": "lead_extraction.txt",
    "RECEIPT": "receipt_extraction.txt",
    "DELIVERY_NOTE": "delivery_note_extraction.txt",
    "CREDIT_NOTE": "credit_note_extraction.txt",
    "DEBIT_NOTE": "debit_note_extraction.txt",
    "PAYMENT_RECEIPT": "payment_receipt_extraction.txt",
    "RFQ": "rfq_extraction.txt",
    "OTHER": "other_extraction.txt"
}

class ExtractionService:
    async def extract_fields(self, document_type: str, redacted_text: str) -> Tuple[Dict[str, Any], Dict[str, float], bool]:
        """Extracts structured fields using specialized prompt template and LLM."""
        prompt_filename = PROMPT_FILE_MAP.get(document_type, "other_extraction.txt")
        prompt_path = os.path.join(PROMPT_DIR, prompt_filename)

        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                template = f.read()
        else:
            template = "Extract structured fields from:\n{redacted_text}"

        prompt = template.format(redacted_text=redacted_text[:4000])

        extracted_data = await llm_service.generate_json(prompt)
        if not isinstance(extracted_data, dict):
            extracted_data = {}

        # Compute field-level confidences
        field_confidences = {}
        missing_count = 0
        total_fields = max(len(extracted_data), 1)

        for key, val in extracted_data.items():
            if val is None or val == "" or val == []:
                field_confidences[key] = 0.0
                missing_count += 1
            else:
                field_confidences[key] = 0.95

        needs_review = (missing_count / total_fields) > 0.4 or len(extracted_data) == 0

        return extracted_data, field_confidences, needs_review

extraction_service = ExtractionService()
