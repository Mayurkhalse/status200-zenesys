from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.db.database import get_mongo_db
from app.core.rbac import get_current_user, UserSession
from app.models.schemas.chat import (
    CreateChatSessionResponse, ChatMessageRequest,
    ChatMessageResponse, ChatSessionItem, ChatMessageItem
)
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service

router = APIRouter(prefix="/chat", tags=["RAG Chatbot"])

@router.post("/sessions", response_model=CreateChatSessionResponse)
async def create_chat_session(current_user: UserSession = Depends(get_current_user)):
    db = get_mongo_db()
    now = datetime.now(timezone.utc)
    session_doc = {
        "user_id": ObjectId(current_user.user_id),
        "messages": [],
        "created_at": now,
        "updated_at": now
    }
    res = await db.chat_sessions.insert_one(session_doc)
    return CreateChatSessionResponse(session_id=str(res.inserted_id))

@router.get("/sessions/{session_id}", response_model=ChatSessionItem)
async def get_chat_session(session_id: str, current_user: UserSession = Depends(get_current_user)):
    db = get_mongo_db()
    sess = await db.chat_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": ObjectId(current_user.user_id)
    })
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found")

    messages = [
        ChatMessageItem(
            role=m["role"],
            content=m["content"],
            source_document_ids=[str(d) for d in m.get("source_document_ids", [])],
            retrieval_method=m.get("retrieval_method"),
            created_at=m["created_at"]
        ) for m in sess.get("messages", [])
    ]

    return ChatSessionItem(
        id=str(sess["_id"]),
        user_id=str(sess["user_id"]),
        messages=messages,
        created_at=sess["created_at"],
        updated_at=sess["updated_at"]
    )

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: str,
    req: ChatMessageRequest,
    current_user: UserSession = Depends(get_current_user)
):
    db = get_mongo_db()
    sess_oid = ObjectId(session_id)
    sess = await db.chat_sessions.find_one({
        "_id": sess_oid,
        "user_id": ObjectId(current_user.user_id)
    })
    if not sess:
        raise HTTPException(status_code=404, detail="Chat session not found")

    now = datetime.now(timezone.utc)
    user_msg_entry = {
        "role": "user",
        "content": req.content,
        "source_document_ids": [],
        "retrieval_method": None,
        "created_at": now
    }

    # Run hybrid retrieval
    source_doc_ids, context_str = await retrieval_service.hybrid_search(req.content, top_k=5)

    prompt = f"""You are an ERP Document Intelligence AI Assistant. Answer the user's question accurately based ONLY on the document context provided below. Always cite relevant document IDs if applicable.

CONTEXT FROM DOCUMENTS:
{context_str}

USER QUESTION:
{req.content}

ANSWER:"""

    assistant_answer = await llm_service.generate_completion(prompt)
    if not assistant_answer or assistant_answer == "{}":
        assistant_answer = f"Based on available document records, here is the context matching your query:\n\n{context_str[:500]}"

    assistant_msg_entry = {
        "role": "assistant",
        "content": assistant_answer,
        "source_document_ids": source_doc_ids,
        "retrieval_method": "hybrid",
        "created_at": datetime.now(timezone.utc)
    }

    await db.chat_sessions.update_one(
        {"_id": sess_oid},
        {
            "$push": {"messages": {"$each": [user_msg_entry, assistant_msg_entry]}},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )

    return ChatMessageResponse(
        role="assistant",
        content=assistant_answer,
        source_document_ids=source_doc_ids,
        retrieval_method="hybrid"
    )
