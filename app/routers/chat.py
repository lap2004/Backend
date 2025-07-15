from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.db.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.chat_service import handle_admission_query, handle_student_query
from app.core.security import decode_access_token, get_current_user
from app.db.models.user_model import User

router = APIRouter(tags=["Chat"])

@router.post("/student", response_model=ChatResponse)
async def chat_student(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return await handle_student_query(request.question, db, user)

@router.post("/admission", response_model=ChatResponse)
async def chat_admission(
    request: ChatRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
):
    auth_header: Optional[str] = http_request.headers.get("Authorization")
    
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)  
            if payload.get("role") != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Bạn không có quyền truy cập API này.",
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ.",
            )

    return await handle_admission_query(request.question, db)