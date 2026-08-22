import os
import json
from typing import List, Dict, Any
from app.services.llm_service import llm_service

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "prompts", "insight_agent.txt")

class InsightAgent:
    async def generate_insights(
        self,
        document_type: str,
        extracted_fields: Dict[str, Any],
        related_entity: str,
        history: List[Dict[str, Any]],
        aggregate_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generates LLM-judged risks, anomalies, trends, and recommendations."""
        if not os.path.exists(PROMPT_PATH):
            return []

        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            template = f.read()

        prompt = template.format(
            document_type=document_type,
            extracted_fields_json=json.dumps(extracted_fields, indent=2),
            related_entity=related_entity or "Unknown Entity",
            n=len(history),
            history_json=json.dumps(history, indent=2, default=str),
            aggregate_stats_json=json.dumps(aggregate_stats, indent=2, default=str)
        )

        insights = await llm_service.generate_json(prompt)
        if isinstance(insights, list):
            valid_insights = []
            for item in insights:
                if isinstance(item, dict) and "type" in item and "severity" in item and "title" in item:
                    valid_insights.append({
                        "type": item.get("type", "risk"),
                        "severity": item.get("severity", "medium"),
                        "title": str(item.get("title", ""))[:80],
                        "description": str(item.get("description", "")),
                        "related_entity": str(item.get("related_entity", related_entity or "Unknown Entity"))
                    })
            return valid_insights
        return []

insight_agent = InsightAgent()
