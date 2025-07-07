import fitz  # PyMuPDF
from uuid import uuid4
from pathlib import Path

def extract_chunks_from_pdf(pdf_path: str) -> list[dict]:
    doc = fitz.open(pdf_path)
    chunks = []
    filename = Path(pdf_path).name

    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if not text:
            continue

        chunks.append({
            "id": uuid4(),
            "title": f"{filename} – Page {i+1}",
            "content": text,
            "type": "pdf",
            "field": "page",
            "source": "pdf",
            "title_raw": filename,
            "ma_nganh": None,
            "doi_tuong": None,
            "filename": filename,
            "file_type": "pdf",
            "page_number": i + 1,
            "chunk_index": 0,
        })

    return chunks

def extract_all_pdfs(folder_path: str) -> list[dict]:
    all_chunks = []
    folder = Path(folder_path)
    for file in folder.glob("*.pdf"):
        chunks = extract_chunks_from_pdf(str(file))
        all_chunks.extend(chunks)
    return all_chunks
