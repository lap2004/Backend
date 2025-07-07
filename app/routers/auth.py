from fastapi import APIRouter, HTTPException, Depends, Header, Response, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from pytest import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.db.models.user_model import User
from app.db.schemas.user_schema import ChangePasswordSchema, UserCreate, UserLogin, TokenResponse, UserOut
from app.services.auth_service import (
    create_access_token,
    get_current_user,
    verify_password
)
from app.auth.email_utils import generate_random_password
from app.config import settings
from app.core.security import password


from app.auth.email_utils import send_new_password_email
from app.db.models.user_model import User

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db

router = APIRouter(tags=["Auth"])


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "message": "Bạn có token hợp lệ!"
    }

@router.get("/me", response_model=UserOut)
async def get_me(user = Depends(get_current_user)):
    return user

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Kiểm tra email đã tồn tại chưa
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    # Tạo user mới với mật khẩu không mã hóa
    new_user = User(
        email=user.email,
        password=password(user.password),  # dùng password() thay vì hash
        full_name=user.full_name,
        role=user.role if hasattr(user, "role") else "student"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Tạo JWT token
    token = create_access_token({"user_id": str(new_user.id), "role": new_user.role})
    return TokenResponse(access_token=token, role=new_user.role)

@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    # Tìm người dùng theo email
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()

    # Kiểm tra mật khẩu thô (plaintext)
    if not db_user or not verify_password(user.password, db_user.password):  # <-- sửa ở đây
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng"
        )

    # Tạo JWT token
    token = create_access_token({
        "user_id": str(db_user.id),
        "role": db_user.role
    })

    return TokenResponse(
        access_token=token,
        role=db_user.role,
        force_password_change=db_user.force_password_change
    )



@router.post("/logout", tags=["Auth"])
async def logout(response: Response):
    """
    Đăng xuất người dùng. Trả về response cho client xoá token.
    Nếu dùng cookie, có thể xoá tại đây luôn.
    """
    res = JSONResponse(content={"message": "Đăng xuất thành công!"})

    # Nếu bạn lưu token trong cookie:
    res.delete_cookie("access_token")

    return res

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    # 🔍 Tìm user theo email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại")

    # 🔐 Tạo mật khẩu ngẫu nhiên mới
    new_password = generate_random_password()

    # ✅ Gán lại mật khẩu mới (plaintext)
    user.password = password(new_password)  # dùng hàm password(), hiện đang trả về nguyên string

    # ✅ Đặt cờ bắt buộc đổi mật khẩu sau khi đăng nhập
    user.force_password_change = True

    # 💾 Cập nhật dữ liệu
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 📧 Gửi email chứa mật khẩu mới
    send_new_password_email(user.email, new_password)

    return {"message": "🔐 Mật khẩu mới đã được gửi đến email của bạn."}

@router.post("/change-password")
async def change_password(
    data: ChangePasswordSchema,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Kiểm tra mật khẩu hiện tại (so sánh plaintext)
    if not verify_password(data.current_password, user.password):  
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng.")

    # Gán mật khẩu mới (không hash)
    user.password = password(data.new_password)  # dùng hàm password(), hiện đang trả lại nguyên chuỗi

    # Tắt cờ bắt đổi mật khẩu
    user.force_password_change = False

    # Lưu thay đổi
    db.add(user)
    await db.commit()

    return {"message": "✅ Đổi mật khẩu thành công"}
