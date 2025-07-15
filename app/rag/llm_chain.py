import google.generativeai as genai
from app.config import settings
from loguru import logger

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

def format_prompt(question: str, contexts: list[dict]) -> str:
    context_texts = [chunk["content"].strip() for chunk in contexts if chunk.get("content")]
    context_block = "\n".join(context_texts)

    return f"""Bạn là trợ lý AI hỗ trợ thông tin tuyển sinh và đào tạo cho Trường Đại học Văn Lang.

Hướng dẫn:
- Nếu người dùng hỏi bằng tiếng Việt → trả lời bằng tiếng Việt.
- Nếu người dùng hỏi bằng tiếng Anh → trả lời bằng tiếng Anh.
- Trả lời ngắn gọn, chính xác, rõ ràng, dễ hiểu.
- Nếu có nhiều ý → trình bày bằng danh sách có đánh số (1., 2., 3...) hoặc gạch đầu dòng đơn giản (-).
- Không nhắc lại "Nội dung tham khảo".
- Nếu câu hỏi không rõ → yêu cầu người dùng hỏi cụ thể hơn.
- Nếu chỉ là lời chào → trả lời thân thiện.
- Bạn **không** được sử dụng bất kỳ định dạng Markdown nào như **chữ in đậm**, *in nghiêng*, hoặc danh sách đánh dấu bằng dấu `*`. Chỉ sử dụng văn bản thuần túy.

Nội dung tham khảo:
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
