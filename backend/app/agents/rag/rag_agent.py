import os
import json
import time
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone
from bson import ObjectId
from app.db.database import get_mongo_db
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service

SYSTEM_PROMPT = """
You are the IntelliParse RAG Reasoning Agent.
Your role is to answer user queries using retrieved document contexts, multi-turn conversation memory, and structured reasoning.

Rules:
1. Base your answers strictly on the retrieved document snippets provided.
2. If the snippets do not contain enough information, state clearly what is missing.
3. Include clear citations (e.g., [Doc ID ...]) when referencing facts.
"""

class RAGReasoningAgent:
    def __init__(self):
        self.agent_id = "agent_rag_01"
        self.agent_name = "RAG Chat Reasoning Agent"
        self.version = "1.2.0"

    async def process_query(self, session_id: str, query: str, user_id: str) -> Dict[str, Any]:
        """Runs RAG hybrid retrieval -> session context synthesis -> LLM response -> persistent history update."""
        start_time = time.time()
        db = get_mongo_db()
        sess_oid = ObjectId(session_id)

        # 1. Fetch Session Memory
        session = await db.chat_sessions.find_one({"_id": sess_oid, "user_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id})
        if not session:
            session = {
                "_id": sess_oid,
                "user_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id,
                "messages": []
            }

        history_snippets = []
        for msg in session.get("messages", [])[-6:]:
            history_snippets.append(f"{msg['role'].upper()}: {msg['content']}")
        history_context = "\n".join(history_snippets)

        # 2. Hybrid Semantic Vector + Keyword Search
        source_doc_ids, context_str = await retrieval_service.hybrid_search(query, top_k=5)

        # 3. Construct Agent Prompt
        agent_prompt = f"""
{SYSTEM_PROMPT}

CONVERSATION HISTORY:
{history_context if history_context else 'None'}

RETRIEVED DOCUMENT SNIPPETS:
{context_str}

USER QUERY:
{query}

ANSWER:
"""

        answer = await llm_service.generate_completion(agent_prompt)
        if not answer or answer == "{}" or not answer.strip():
            answer = f"Based on your document repository context:\n\n{context_str}"

        now = datetime.now(timezone.utc)

        user_msg = {
            "role": "user",
            "content": query,
            "created_at": now
        }
        assistant_msg = {
            "role": "assistant",
            "content": answer,
            "source_document_ids": [ObjectId(d) for d in source_doc_ids if ObjectId.is_valid(d)],
            "retrieval_method": "hybrid_pgvector_bm25",
            "created_at": now
        }

        # 4. Save Session Messages
        await db.chat_sessions.update_one(
            {"_id": sess_oid},
            {
                "$set": {"updated_at": now},
                "$push": {"messages": {"$each": [user_msg, assistant_msg]}}
            },
            upsert=True
        )

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # 5. Log Trace
        await db.agent_traces.insert_one({
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "session_id": session_id,
            "user_id": user_id,
            "query_length": len(query),
            "sources_found": len(source_doc_ids),
            "latency_ms": latency_ms,
            "timestamp": now
        })

        return {
            "role": "assistant",
            "content": answer,
            "source_document_ids": source_doc_ids,
            "retrieval_method": "hybrid_pgvector_bm25",
            "created_at": now
        }

rag_reasoning_agent = RAGReasoningAgent()
