import uuid
from datetime import datetime

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> str:
    return datetime.utcnow().isoformat()

def truncate_text(text: str, max_length: int = 200) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
