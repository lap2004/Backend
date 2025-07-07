from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.core.constants import Role
from app.db.models.user_model import User
from app.db.database import get_db  # bạn cần import get_db để truy vấn DB

# Mật khẩu và Token
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

# Trả lại mật khẩu thô (plaintext)
def password(password: str) -> str:
    return password  # không mã hóa gì cả

# So sánh trực tiếp mật khẩu người dùng nhập với mật khẩu lưu trong DB
def verify_password(plain_password: str, stored_password: str) -> bool:
    return plain_password == stored_password

# Giải mã token
def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ",
        )

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thiếu hoặc sai định dạng Authorization header",
        )

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token thiếu thông tin")

    # 🔍 Truy vấn người dùng từ DB
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    return user  

# Kiểm tra quyền người dùng
def require_role(allowed_roles: list[Role]):
    """
    Dependency kiểm tra xem người dùng hiện tại có nằm trong danh sách quyền không.
    """
    async def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập chức năng này."
            )
        return current_user

    return checker
