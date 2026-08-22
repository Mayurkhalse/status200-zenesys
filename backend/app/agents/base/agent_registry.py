from typing import Dict
from app.agents.base.base_agent import BaseAgent
from app.agents.specialized.invoice_agent import InvoiceAgent
from app.agents.specialized.po_agent import PurchaseOrderAgent, SalesOrderAgent
from app.agents.specialized.contract_agent import ContractAgent, LeadAgent
from app.agents.specialized.other_agents import (
    QuotationAgent, ProposalAgent, ReceiptAgent,
    DeliveryNoteAgent, NoteAgent, RFQAgent, GenericDocumentAgent
)

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._register_default_agents()

    def _register_default_agents(self):
        self.register(InvoiceAgent())
        self.register(PurchaseOrderAgent())
        self.register(SalesOrderAgent())
        self.register(ContractAgent())
        self.register(LeadAgent())
        self.register(QuotationAgent())
        self.register(ProposalAgent())
        self.register(ReceiptAgent())
        self.register(DeliveryNoteAgent())
        self.register(NoteAgent("CREDIT_NOTE"))
        self.register(NoteAgent("DEBIT_NOTE"))
        self.register(RFQAgent())
        self.register(GenericDocumentAgent())

    def register(self, agent: BaseAgent):
        """Registers a specialized agent instance."""
        self._agents[agent.document_type] = agent
        print(f"Registered AI Agent: {agent.agent_name} [{agent.agent_id}] for type '{agent.document_type}'")

    def get_agent(self, document_type: str) -> BaseAgent:
        """Retrieves specialized agent by document type, falling back to GenericDocumentAgent."""
        return self._agents.get(document_type, self._agents.get("OTHER", GenericDocumentAgent()))

agent_registry = AgentRegistry()
