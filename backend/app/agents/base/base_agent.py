import os
import time
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from bson import ObjectId
from app.db.database import get_mongo_db
from app.services.llm_service import llm_service

PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "specialized", "prompts")

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_name: str, document_type: str, prompt_filename: str, version: str = "1.0.0"):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.document_type = document_type
        self.prompt_filename = prompt_filename
        self.version = version

    def load_prompt_template(self) -> str:
        """Reads system prompt template file from disk."""
        prompt_path = os.path.join(PROMPT_DIR, self.prompt_filename)
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return "Extract structured JSON fields from:\n{redacted_text}"

    @abstractmethod
    def validate_schema(self, extracted_data: Dict[str, Any]) -> Tuple[bool, list]:
        """Custom schema & sanity checks per document type."""
        pass

    async def reflect_and_correct(self, redacted_text: str, raw_json: Dict[str, Any], errors: list) -> Dict[str, Any]:
        """Self-reflection loop: asks LLM to fix schema validation errors."""
        reflection_prompt = f"""
You are an AI Agent self-correction supervisor. 
The previous extraction output produced validation errors:
{json.dumps(errors, indent=2)}

Original Raw Extracted Output:
{json.dumps(raw_json, indent=2)}

Document Text:
{redacted_text[:3000]}

Correct the JSON fields strictly adhering to the valid schema. Return ONLY valid JSON.
"""
        corrected = await llm_service.generate_json(reflection_prompt)
        return corrected if isinstance(corrected, dict) else raw_json

    async def execute(self, redacted_text: str, document_id: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, float], bool]:
        """Runs end-to-end agent pipeline: Prompt -> LLM -> Validation -> Self-Reflection -> Trace Logging."""
        start_time = time.time()
        template = self.load_prompt_template()
        prompt = template.replace("{redacted_text}", redacted_text[:4000])

        # Step 1: Initial LLM Generation
        extracted_data = await llm_service.generate_json(prompt)
        if not isinstance(extracted_data, dict):
            extracted_data = {}

        # Step 2: Schema Validation
        is_valid, errors = self.validate_schema(extracted_data)

        # Step 3: Self-Reflection loop if validation failed
        reflection_applied = False
        if not is_valid:
            extracted_data = await self.reflect_and_correct(redacted_text, extracted_data, errors)
            reflection_applied = True

        # Step 4: Field-level confidence scores
        confidences = {}
        missing_count = 0
        total_fields = max(len(extracted_data), 1)

        for k, v in extracted_data.items():
            if v is None or v == "" or v == []:
                confidences[k] = 0.0
                missing_count += 1
            else:
                confidences[k] = 0.95 if not reflection_applied else 0.85

        needs_review = (missing_count / total_fields) > 0.4 or len(extracted_data) == 0

        execution_latency_ms = round((time.time() - start_time) * 1000, 2)

        # Step 5: Persistent Agent Trace Logging
        await self._log_agent_trace(
            document_id=document_id,
            input_text_length=len(redacted_text),
            extracted_keys=list(extracted_data.keys()),
            validation_errors=errors,
            reflection_applied=reflection_applied,
            execution_latency_ms=execution_latency_ms
        )

        return extracted_data, confidences, needs_review

    async def _log_agent_trace(
        self,
        document_id: Optional[str],
        input_text_length: int,
        extracted_keys: list,
        validation_errors: list,
        reflection_applied: bool,
        execution_latency_ms: float
    ):
        """Stores agent execution trace in MongoDB for auditing."""
        try:
            db = get_mongo_db()
            trace_doc = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "document_type": self.document_type,
                "version": self.version,
                "document_id": ObjectId(document_id) if document_id and ObjectId.is_valid(document_id) else document_id,
                "input_text_length": input_text_length,
                "extracted_keys_count": len(extracted_keys),
                "validation_errors": validation_errors,
                "reflection_applied": reflection_applied,
                "execution_latency_ms": execution_latency_ms,
                "timestamp": datetime.now(timezone.utc)
            }
            await db.agent_traces.insert_one(trace_doc)
        except Exception as e:
            print(f"Agent trace logging note: {e}")
