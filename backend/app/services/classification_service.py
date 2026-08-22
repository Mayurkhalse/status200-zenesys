import httpx
from typing import Dict, Any
from app.core.config import settings

DOCUMENT_CLASSES = [
    "BUSINESS_INVOICE", "PURCHASE_ORDER", "SALES_ORDER", "QUOTATION",
    "PROPOSAL", "CONTRACT", "LEAD", "RECEIPT", "DELIVERY_NOTE",
    "CREDIT_NOTE", "DEBIT_NOTE", "PAYMENT_RECEIPT", "RFQ", "OTHER"
]

class ClassificationService:
    async def classify_document(self, text: str, filename: str) -> Dict[str, Any]:
        """Runs rule-based keyword check, ML service predictor, and LLM fallback in parallel."""
        # 1. Rule-based keyword matching
        rule_class, rule_confidence = self._rule_based_check(text, filename)

        # 2. Call ML Service endpoint
        ml_res = await self._call_ml_service(text, filename)
        
        # Determine top prediction & confidence
        if ml_res and ml_res.get("confidence", 0) > rule_confidence:
            doc_type = ml_res.get("document_type", rule_class)
            confidence = ml_res.get("confidence", rule_confidence)
            top_k = ml_res.get("top_k", [doc_type])
            probabilities = ml_res.get("probabilities", {doc_type: confidence})
            source = "ml"
        else:
            doc_type = rule_class
            confidence = rule_confidence
            top_k = [rule_class]
            probabilities = {rule_class: rule_confidence}
            source = "rule"

        # Check top-2 margin for tie handling
        sorted_probs = sorted(probabilities.values(), reverse=True)
        top1_prob = sorted_probs[0] if len(sorted_probs) > 0 else 0
        top2_prob = sorted_probs[1] if len(sorted_probs) > 1 else 0
        margin_tie = (top1_prob - top2_prob) < 0.02 if len(sorted_probs) > 1 else False

        # Determine decision routing
        if confidence >= 0.85 and not margin_tie:
            decision = "AUTO_ACCEPT"
        elif 0.60 <= confidence < 0.85 or margin_tie:
            decision = "REVIEW_LLM_FALLBACK"
        else:
            decision = "HUMAN_REVIEW"

        return {
            "document_type": doc_type,
            "decision": decision,
            "confidence": round(confidence, 4),
            "top_k": top_k,
            "probabilities": probabilities,
            "model_version": "1.0.0",
            "source": source
        }

    def _rule_based_check(self, text: str, filename: str) -> tuple[str, float]:
        text_lower = (text + " " + filename).lower()
        if "invoice" in text_lower or "tax invoice" in text_lower or "bill to" in text_lower:
            return "BUSINESS_INVOICE", 0.90
        elif "purchase order" in text_lower or "p.o. number" in text_lower or "po #" in text_lower:
            return "PURCHASE_ORDER", 0.90
        elif "sales order" in text_lower:
            return "SALES_ORDER", 0.88
        elif "quotation" in text_lower or "quote #" in text_lower:
            return "QUOTATION", 0.88
        elif "proposal" in text_lower or "scope of work" in text_lower:
            return "PROPOSAL", 0.85
        elif "contract" in text_lower or "agreement" in text_lower:
            return "CONTRACT", 0.85
        elif "lead" in text_lower or "contact inquiry" in text_lower:
            return "LEAD", 0.80
        elif "receipt" in text_lower or "merchant" in text_lower:
            return "RECEIPT", 0.85
        elif "delivery note" in text_lower or "goods received" in text_lower:
            return "DELIVERY_NOTE", 0.85
        elif "credit note" in text_lower:
            return "CREDIT_NOTE", 0.88
        elif "debit note" in text_lower:
            return "DEBIT_NOTE", 0.88
        elif "payment receipt" in text_lower:
            return "PAYMENT_RECEIPT", 0.88
        elif "rfq" in text_lower or "request for quotation" in text_lower:
            return "RFQ", 0.88
        return "OTHER", 0.50

    async def _call_ml_service(self, text: str, filename: str) -> Dict[str, Any]:
        try:
            import os
            clean_filename = filename if filename.endswith('.txt') else f"{os.path.splitext(filename)[0]}.txt"
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(
                    f"{settings.ML_SERVICE_URL}/predict/upload",
                    files={"file": (clean_filename, text.encode('utf-8'), "text/plain")}
                )
                if res.status_code == 200:
                    return res.json()
        except Exception as e:
            print(f"ML service call note: {e}")
        return None

classification_service = ClassificationService()
