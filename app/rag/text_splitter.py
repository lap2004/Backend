import tiktoken
from typing import List
from uuid import uuid4

# Load tokenizer theo model 
ENCODING_NAME = "cl100k_base"  
tokenizer = tiktoken.get_encoding(ENCODING_NAME)

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))

def split_text_by_tokens(text: str, max_tokens: int = 500, min_tokens: int = 200) -> List[str]:
    tokens = tokenizer.encode(text)
    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        if len(chunk_tokens) >= min_tokens or end == len(tokens):
            chunk_text = tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text.strip())
        start += max_tokens

    return chunks

def split_chunk_if_needed(chunk: dict, max_tokens=500, min_tokens=200) -> List[dict]:
    splits = split_text_by_tokens(chunk["content"], max_tokens, min_tokens)
    results = []

    for i, text in enumerate(splits):
        new_chunk = chunk.copy()
        new_chunk["id"] = uuid4()
        new_chunk["content"] = text
        new_chunk["chunk_index"] = i
        results.append(new_chunk)

    return results
