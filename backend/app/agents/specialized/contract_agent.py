from typing import Dict, Any, Tuple
from app.agents.base.base_agent import BaseAgent

class ContractAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent_contract_04",
            agent_name="Contract & Legal Agreement Agent",
            document_type="CONTRACT",
            prompt_filename="contract_extraction.txt",
            version="1.1.0"
        )

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        errors = []
        if not data.get("title") and not data.get("contract_number"):
            errors.append("Missing contract title or number")
        if not data.get("parties"):
            errors.append("Missing contracting parties")
        return len(errors) == 0, errors

class LeadAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent_lead_05",
            agent_name="CRM Lead Extraction Agent",
            document_type="LEAD",
            prompt_filename="lead_extraction.txt",
            version="1.1.0"
        )

    def validate_schema(self, data: Dict[str, Any]) -> Tuple[bool, list]:
        errors = []
        if not data.get("lead_name") and not data.get("company"):
            errors.append("Missing lead name or company name")
        return len(errors) == 0, errors
