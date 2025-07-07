from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from typing import List

class EmbeddingRecordSchema(BaseModel):
    id: UUID
    title: str
    content: str
    type: Optional[str] = None
    field: Optional[str] = None
    source: Optional[str] = None
    ma_nganh: Optional[str] = None
    doi_tuong: Optional[str] = None
    chunk_index: Optional[int] = None
    created_at: Optional[datetime] = None
    embedding: Optional[List[float]] = None  

    model_config = {
        "from_attributes": True
    }
