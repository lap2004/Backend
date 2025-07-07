from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings

serializer = URLSafeTimedSerializer(settings.JWT_SECRET_KEY)
def generate_reset_token(email: str) -> str:
    return serializer.dumps(email, salt="reset-password")

def verify_reset_token(token: str, max_age: int = 3600) -> str:
    try:
        return serializer.loads(token, salt="reset-password", max_age=max_age)
    except Exception:
        raise ValueError("Token đặt lại mật khẩu không hợp lệ hoặc đã hết hạn")
    
    