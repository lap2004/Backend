from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Literal

TABLE_BY_ROLE = {
    "guest": "embedding_admissions_20250709",
    "admission": "embedding_admissions_20250709",
    "student": """
        (
            SELECT id, content, title, source, field, type, chunk_index, embedding FROM embedding_admissions_20250709
            UNION ALL
            SELECT id, content, title, source, field, type, chunk_index, embedding FROM embedding_students_20250709
            UNION ALL
            SELECT id, content, title, source, field, type, chunk_index, embedding FROM embedding_pdfs_20250709
        )
    """
}


async def retrieve_chunks(
    embedding: list[float],
    role: Literal["guest", "student"],
    db: AsyncSession,
    top_k: int = 20,
    field: str = "",
    type_: str = ""
):
    """
    Truy vấn các đoạn văn phù hợp nhất từ vector embedding theo vai trò người dùng.

    Args:
        embedding: vector nhúng của câu hỏi.
        role: 'guest' hoặc 'student' để quyết định bảng truy vấn.
        db: phiên kết nối async với database.
        top_k: số đoạn kết quả trả về.
        field: lọc theo trường 'field' nếu có.
        type_: lọc theo trường 'type' nếu có.

    Returns:
        Danh sách dict chứa các đoạn văn và điểm tương đồng.
    """
    table_expr = TABLE_BY_ROLE.get(role)
    if not table_expr:
        raise ValueError(f"Role không hợp lệ: {role}")

    filters = []
    if field:
        filters.append("field = :field")
    if type_:
        filters.append("type = :type")
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    sql = text(f"""
        SELECT id, content, title, source, field, type, chunk_index,
               1 - (embedding <#> (:embedding)::vector) AS score
        FROM {table_expr} AS sub
        {where_clause}
        ORDER BY embedding <#> (:embedding)::vector
        LIMIT :top_k
    """)
    params = {
        "embedding": f"[{', '.join(map(str, embedding))}]",
        "top_k": top_k,
    }
    if field:
        params["field"] = field
    if type_:
        params["type"] = type_

    result = await db.execute(sql, params)
    rows = result.fetchall()

    return [
        {
            "id": row.id,
            "title": row.title,
            "content": row.content,
            "source": row.source,
            "field": row.field,
            "type": row.type,
            "chunk_index": row.chunk_index,
            "score": row.score,
        }
        for row in rows
    ]
