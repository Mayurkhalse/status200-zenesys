from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ChatMessageRequest(BaseModel):
    content: str

class ChatMessageItem(BaseModel):
    role: str  # user | assistant
    content: str
    source_document_ids: List[str] = []
    retrieval_method: Optional[str] = None  # semantic | keyword | hybrid
    created_at: datetime

class ChatSessionItem(BaseModel):
    id: str
    user_id: str
    messages: List[ChatMessageItem] = []
    created_at: datetime
    updated_at: datetime

class CreateChatSessionResponse(BaseModel):
    session_id: str

class ChatMessageResponse(BaseModel):
    role: str = "assistant"
    content: str
    source_document_ids: List[str] = []
    retrieval_method: str = "hybrid"
