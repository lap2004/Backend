from typing import Optional
from uuid import UUID
from app.rag.retriever import retrieve_chunks
from app.rag.llm_chain import ask_gemini
from app.config import settings
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.chat_model import ChatHistory

# model = SentenceTransformer(settings.EMBED_MODEL_NAME)
model = SentenceTransformer(settings.EMBED_MODEL_NAME, device="cpu")

# async def chat_pipeline(
async def chat_pipeline(
    question: str,
    role: str,
    db: AsyncSession,
    top_k: int = 20,
    filter_field: str = "",
    filter_type: str = "",
    user_id: Optional[UUID] = None,
    username: str = "guest"
) -> dict:
    query_vector = model.encode(question, normalize_embeddings=True).tolist()
    
    chunks = await retrieve_chunks(
        embedding=query_vector,
        role=role,
        db=db,
        top_k=top_k,
        field=filter_field,
        type_=filter_type
    )

    answer = ask_gemini(question, chunks)
    history = ChatHistory(
        user_id=user_id,
        username=username,
        role=role,
        question=question,
        answer=answer,
    )
    db.add(history)
    await db.commit()

    return {
        "answer": answer,
        "chunks": chunks
    }
