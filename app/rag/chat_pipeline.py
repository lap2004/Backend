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
#     question: str,
#     role: str,
#     db: AsyncSession,
#     top_k: int = 20,
#     filter_field: str = "",
#     filter_type: str = ""
# ) -> dict:
#     query_vector = model.encode(question, normalize_embeddings=True).tolist()
#     chunks = await retrieve_chunks(
#         embedding=query_vector,
#         role=role,
#         db=db,
#         top_k=top_k,
#         field=filter_field,
#         type_=filter_type
#     )

#     answer = ask_gemini(question, chunks)
#     return {
#         "answer": answer,
#         "chunks": chunks 
#     }

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

    # ✅ Ghi log vào chat_history
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

# from app.rag.retriever import retrieve_chunks
# from app.rag.llm_chain import ask_gemini
# from app.config import settings
# from sentence_transformers import SentenceTransformer
# from sqlalchemy.ext.asyncio import AsyncSession

# # Load model embedding (dùng CPU nếu thiếu RAM GPU)
# model = SentenceTransformer(settings.EMBED_MODEL_NAME, device="cpu")

# async def chat_pipeline(
#     question: str,
#     role: str,
#     db: AsyncSession,
#     top_k: int = 20,
#     filter_field: str = "",
#     filter_type: str = "",
#     return_contexts: bool = False  # flag để tùy chọn trả contexts
# ) -> dict:
#     # Bước 1: embedding câu hỏi
#     query_vector = model.encode(question, normalize_embeddings=True).tolist()

#     # Bước 2: truy hồi chunk liên quan
#     chunks = await retrieve_chunks(
#         embedding=query_vector,
#         role=role,
#         db=db,
#         top_k=top_k,
#         field=filter_field,
#         type_=filter_type
#     )

#     # Bước 3: gọi LLM sinh câu trả lời
#     answer = await ask_gemini(question, chunks)  # ⚠️ ensure ask_gemini is async

#     # Bước 4: trả kết quả
#     result = {"answer": answer}
#     if return_contexts:
#         result["contexts"] = chunks
#     return result
