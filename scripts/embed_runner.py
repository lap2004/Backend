from app.rag.processor_json import load_json_chunks
from app.rag.processor_pdf import extract_all_pdfs
from app.rag.text_splitter import split_chunk_if_needed
from app.rag.embedder import embed_chunks
from app.config import settings

def process_and_embed(source_name: str, raw_chunks: list[dict], table_name: str):
    all_chunks = []
    for chunk in raw_chunks:
        splits = split_chunk_if_needed(chunk, max_tokens=500, min_tokens=200)
        all_chunks.extend(splits)

    print(f"🔹 Tổng {len(all_chunks)} đoạn sau khi chia (source: {source_name})")
    embed_chunks(all_chunks, table_name=table_name)

def main():
    print("Bắt đầu embedding toàn bộ dữ liệu...")

    admission_chunks = load_json_chunks(settings.DATA_PATH_ADMISSIONS, source="admissions")
    process_and_embed("admissions", admission_chunks, table_name="embedding_admissions_20250715")

    student_chunks = load_json_chunks(settings.DATA_PATH_STUDENTS, source="students")
    process_and_embed("students", student_chunks, table_name="embedding_students_20250715")

    pdf_chunks = extract_all_pdfs(settings.PDF_DIR)
    process_and_embed("pdfs", pdf_chunks, table_name="embedding_pdfs_20250715")

    print(" Hoàn tất embedding tất cả nguồn dữ liệu.")

if __name__ == "__main__":
    main()
