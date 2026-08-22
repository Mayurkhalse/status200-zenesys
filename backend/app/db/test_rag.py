import asyncio
from app.db.database import init_db, get_mongo_db
from app.agents.rag.rag_agent import rag_reasoning_agent
from app.services.retrieval_service import retrieval_service

async def main():
    await init_db()
    db = get_mongo_db()

    # Index document for RAG search
    doc_text = "BUSINESS INVOICE # INV-9921\nVendor: Global Logistics Inc\nAmount: $15,400.00\nPayment Terms: Net 30\nDue Date: 2026-09-30"
    await retrieval_service.index_document("doc_rag_test_101", doc_text)

    # Process query
    sess_id = "60f1a9b2c3d4e5f6a7b8c9d0"
    res = await rag_reasoning_agent.process_query(
        session_id=sess_id,
        query="What is the total amount and due date for Global Logistics invoice?",
        user_id="user_test_01"
    )

    print("=== RAG AGENT TEST SUCCESS ===")
    print("Response:", res["content"])
    print("Sources Found:", res["source_document_ids"])

if __name__ == "__main__":
    asyncio.run(main())
