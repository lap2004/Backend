import json
import os
import re

WORD_FILTER_PATH = os.path.join("data", "word_filter.json")
with open(WORD_FILTER_PATH, "r", encoding="utf-8") as f:
    raw_phrases = list(json.load(f).keys())

FORBIDDEN_PHRASES = [phrase.replace("_", " ").lower() for phrase in raw_phrases]

FORBIDDEN_PATTERNS = [
    re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)", re.IGNORECASE)
    for phrase in FORBIDDEN_PHRASES
]

def normalize_question(text: str) -> str:
    return text.lower().strip()

def is_question_safe(question: str) -> bool:
    """
    Trả về False nếu câu hỏi chứa cụm từ bị cấm đúng nguyên vẹn
    """
    normalized = normalize_question(question)
    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(normalized):
            return False
    return True

