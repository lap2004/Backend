from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_db
from app.db.models.user_model import User
from app.db.schemas.user_schema import ChangePasswordSchema, GoogleLoginRequest, UserCreate, UserLogin, TokenResponse, UserOut
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
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    new_user = User(
        email=user.email,
        password=password(user.password),
        full_name=user.full_name,
        role=user.role if hasattr(user, "role") else "student"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token({"user_id": str(new_user.id), "role": new_user.role})
    return TokenResponse(access_token=token, role=new_user.role)


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng"
        )

    token = create_access_token({
        "user_id": str(db_user.id),
        "role": db_user.role
    })

    response = JSONResponse(content={
        "access_token": token,
        "role": db_user.role,
        "force_password_change": db_user.force_password_change
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="Lax",  
        max_age=60 * 60 * 24 * 7,  
        secure=False 
    )

    return response

@router.post("/logout", tags=["Auth"])
async def logout(response: Response):
    res = JSONResponse(content={"message": "Đăng xuất thành công!"})
    res.delete_cookie("access_token")
    return res

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Email không tồn tại")

    new_password = generate_random_password()

    user.password = password(new_password)  
    user.force_password_change = True

    db.add(user)
    await db.commit()
    await db.refresh(user)
    send_new_password_email(user.email, new_password)

    return {"message": "Mật khẩu mới đã được gửi đến email của bạn."}

@router.post("/change-password")
async def change_password(
    data: ChangePasswordSchema,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.current_password, user.password):  
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng.")

    user.password = password(data.new_password) 
    user.force_password_change = False

    db.add(user)
    await db.commit()

    return {"message": "Đổi mật khẩu thành công"}

@router.post("/google")
async def login_google(data: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    try:
        id_info = google_id_token.verify_oauth2_token(
            data.id_token, google_requests.Request()
        )
        email = id_info.get("email")
        name = id_info.get("name", "")
        if not email:
            raise ValueError("Token không chứa email")
    except Exception:
        raise HTTPException(status_code=401, detail="id_token không hợp lệ")

    result = await db.execute(select(User).where(User.email == email))
    db_user = result.scalar_one_or_none()

    if not db_user:
        db_user = User(
            email=email,
            full_name=name,
            password="google-auth",  
            role="student",
            force_password_change=False
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

    token = create_access_token({
        "user_id": str(db_user.id),
        "role": db_user.role
    })

    response = JSONResponse(content={
        "access_token": token,
        "role": db_user.role,
        "force_password_change": db_user.force_password_change
    })
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,
        secure=False
    )
    return response