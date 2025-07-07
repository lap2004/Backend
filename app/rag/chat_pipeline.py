from app.rag.retriever import retrieve_chunks
from app.rag.llm_chain import ask_gemini
from app.config import settings
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession

# Load model embedding 1 lần
model = SentenceTransformer(settings.EMBED_MODEL_NAME)

async def chat_pipeline(
    question: str,
    role: str,
    db: AsyncSession,
    top_k: int = 20,
    filter_field: str = "",
    filter_type: str = ""
) -> dict:
    """
    Pipeline xử lý câu hỏi người dùng:
    - Tạo embedding
    - Truy vấn vector
    - Gửi lên Gemini
    - Trả về câu trả lời

    Returns:
        dict chứa answer, source_chunks
    """
    # 1. Tạo embedding cho câu hỏi
    query_vector = model.encode(question, normalize_embeddings=True).tolist()

    # 2. Truy vấn top-k đoạn phù hợp
    chunks = await retrieve_chunks(
        embedding=query_vector,
        role=role,
        db=db,
        top_k=top_k,
        field=filter_field,
        type_=filter_type
    )

    # 3. Gọi LLM sinh câu trả lời
    answer = ask_gemini(question, chunks)

    # 4. Trả về kèm source
    return {
        "answer": answer,
        "chunks": chunks 
    }
