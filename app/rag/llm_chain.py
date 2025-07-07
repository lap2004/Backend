import google.generativeai as genai
from app.config import settings
from loguru import logger

# Cấu hình Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

def format_prompt(question: str, contexts: list[dict]) -> str:
    context_texts = [f"- {chunk['content'].strip()}" for chunk in contexts if chunk.get("content")]
    context_block = "\n".join(context_texts)

    return f"""Bạn là trợ lý AI chuyên nghiệp hỗ trợ thông tin tuyển sinh và đào tạo cho Trường Đại học Văn Lang. Luôn trả lời bằng tiếng Việt, chính xác, ngắn gọn, rõ ràng và xuống dòng hợp lý.

Nếu câu hỏi chỉ là chào hỏi → đáp lại thân thiện.  
Nếu câu hỏi không rõ nghĩa → yêu cầu người dùng hỏi cụ thể hơn.  
Nếu câu hỏi hợp lệ → trả lời chi tiết, theo mẫu danh sách rõ ràng như:
Tiêu đề liên quan
Nội dung:
- Không dùng các kí tự như * và # 
- Gạch đầu dòng
- Xuống dòng đầy đủ
- Dễ đọc
Thông tin tham khảo:
{context_block}

Câu hỏi: {question}
""".strip()


def ask_gemini(question: str, contexts: list[dict]) -> str:
    prompt = format_prompt(question, contexts)

    try:
        response = model.generate_content(prompt)
        answer = response.text.strip()

        if not answer or "không rõ" in answer.lower() or "không hiểu" in answer.lower():
            return " Tôi chưa hiểu rõ câu hỏi của bạn. Bạn có thể hỏi cụ thể hơn không?"

        if question.lower().strip() in ["xin chào", "chào", "hello", "hi"]:
            return "Xin chào! Tôi là AI Chatbot Tuyển sinh của Đại Học Văn Lang. Tôi có thể giúp gì cho bạn."

        return answer

    except Exception as e:
        logger.error(f"Lỗi khi gọi Gemini: {e}")
        return " Rất tiếc, hệ thống đang gặp lỗi. Bạn vui lòng thử lại sau."
