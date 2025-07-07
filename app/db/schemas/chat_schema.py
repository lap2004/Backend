from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ChatRequest(BaseModel):
    question: str

class SourceChunk(BaseModel):
    id: UUID
    title: str
    content: str
    field: Optional[str] = None
    type: Optional[str] = None
    score: Optional[float] = None 

class ChatResponse(BaseModel):
    answer: str
    chunks: Optional[List[SourceChunk]] = None 

class ChatHistoryOut(BaseModel):
    id: UUID
    username: str
    role: str
    question: str
    answer: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }