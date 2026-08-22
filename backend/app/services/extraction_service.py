from typing import Dict, Any, Tuple, Optional
from app.agents.base.agent_registry import agent_registry

class ExtractionService:
    async def extract_fields(
        self,
        document_type: str,
        redacted_text: str,
        document_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Dict[str, float], bool]:
        """Delegates field extraction to dedicated Specialized AI Agent with schema validation and trace logging."""
        agent = agent_registry.get_agent(document_type)
        return await agent.execute(redacted_text, document_id=document_id)

extraction_service = ExtractionService()
