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
from app.agents.rag.rag_agent import rag_reasoning_agent

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
    res = await rag_reasoning_agent.process_query(
        session_id=session_id,
        query=req.content,
        user_id=current_user.user_id
    )

    return ChatMessageResponse(
        role="assistant",
        content=res["content"],
        source_document_ids=res["source_document_ids"],
        retrieval_method=res["retrieval_method"],
        created_at=res["created_at"]
    )
