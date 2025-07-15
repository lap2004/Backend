from collections import defaultdict
import datetime
from typing import List
from fastapi.responses import JSONResponse
from sqlalchemy import select 
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user_model import User
import os
import shutil
import uuid
import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.core.security import password
from app.db.schemas.user_schema import UserOut, UserUpdate
from app.db.models.chat_model import ChatHistory
from app.core.dependencies import get_current_admin_user

router = APIRouter(tags=["Admin"])

DATA_PATH_ADMISSIONS = "data/admissions_20250623.json"
DATA_PATH_STUDENTS = "data/students_20250623.json"
PDF_DIR = "data/static/pdfs"

# @router.get("/stats")
# def get_stats(db: Session = Depends(get_db)):
#     total_users = db.query(User).count()
#     total_students = db.query(User).filter(User.role == "student").count()
#     total_admins = db.query(User).filter(User.role == "admin").count()
#     return {
#         "total_users": total_users,
#         "total_students": total_students,
#         "total_admins": total_admins,
    # }

@router.post("/upload-json")
async def upload_json_append(
    file: UploadFile = File(...),
    type: str = Form(...)
):
    if type not in ["admissions", "students"]:
        raise HTTPException(status_code=400, detail="Loại dữ liệu phải là 'admissions' hoặc 'students'")

    save_path = DATA_PATH_ADMISSIONS if type == "admissions" else DATA_PATH_STUDENTS

    try:
        old_data = []
        if os.path.exists(save_path):
            with open(save_path, "r", encoding="utf-8") as f:
                old_data = json.load(f)

        new_data = json.load(file.file)
        if not isinstance(new_data, list):
            raise HTTPException(status_code=400, detail="File JSON phải là danh sách (array) các đối tượng")

        combined_data = old_data + new_data
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)

        return {
            "message": f"Đã nối dữ liệu vào '{type}' thành công",
            "total_records": len(combined_data)
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="File không phải là JSON hợp lệ")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    os.makedirs(PDF_DIR, exist_ok=True)

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext != ".pdf":
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file PDF")

    filename = file.filename
    save_path = os.path.join(PDF_DIR, filename)

    if os.path.exists(save_path):
        base_name = os.path.splitext(filename)[0]
        unique_name = f"{base_name}_{uuid.uuid4().hex[:8]}.pdf"
        save_path = os.path.join(PDF_DIR, unique_name)

    try:
        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return {"message": "PDF đã được lưu", "filename": os.path.basename(save_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi ghi file: {str(e)}")

@router.put("/{user_id}")
async def update_user(user_id: UUID, data: UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    user.full_name = data.full_name or user.full_name
    user.email = data.email or user.email
    user.role = data.role or user.role
    if data.password:
        user.password = data.password

    await db.commit()
    await db.refresh(user)
    return {"message": "Cập nhật thành công", "user": user}

@router.delete("/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    await db.delete(user)
    await db.commit()
    return {"message": f"Đã xoá người dùng: {user.email}"}


@router.get("/all-users")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

# @router.get("/dashboard")
# def get_admin_dashboard(db: Session = Depends(get_db), admin_user=Depends(get_current_admin_user)):
#     total_users = db.query(User).count()
#     total_students = db.query(User).filter(User.role == "student").count()
#     total_admins = db.query(User).filter(User.role == "admin").count()
#     latest_signup = db.query(User).order_by(User.created_at.desc()).first()

#     today = datetime.utcnow().date()
#     start_date = today - datetime.timedelta(days=6)
#     signup_by_day = (
#         db.query(User.created_at)
#         .filter(User.created_at >= start_date)
#         .all()
#     )

#     signup_counter = defaultdict(int)
#     for user in signup_by_day:
#         day = user.created_at.date().isoformat()
#         signup_counter[day] += 1

#     signup_result = [
#         {"date": (start_date + datetime.timedelta(days=i)).isoformat(), "count": signup_counter[(start_date + datetime.timedelta(days=i)).isoformat()]}
#         for i in range(7)
#     ]

#     chat_by_day = (
#         db.query(ChatHistory.timestamp)
#         .filter(ChatHistory.timestamp >= start_date)
#         .all()
#     )

#     chat_counter = defaultdict(int)
#     for chat in chat_by_day:
#         day = chat.timestamp.date().isoformat()
#         chat_counter[day] += 1

#     chat_result = [
#         {"date": (start_date + datetime.timedelta(days=i)).isoformat(), "questions": chat_counter[(start_date + datetime.timedelta(days=i)).isoformat()]}
#         for i in range(7)
#     ]

#     return {
#         "summary": {
#             "total_users": total_users,
#             "total_students": total_students,
#             "total_admins": total_admins,
#             "latest_signup": latest_signup.created_at.date().isoformat() if latest_signup else "N/A"
#         },
#         "signup_by_day": signup_result,
#         "chat_usage": chat_result
#     }

@router.get("/stats")
async def get_admin_stats(db: AsyncSession = Depends(get_db)):
    try:
        # Tổng số người dùng
        total_users = await db.scalar(text("SELECT COUNT(*) FROM user_20250627"))

        # Tổng lượt hỏi theo vai trò
        student_chats = await db.scalar(text("SELECT COUNT(*) FROM chat_history WHERE role = 'student'"))
        admission_chats = await db.scalar(text("SELECT COUNT(*) FROM chat_history WHERE role = 'admission'"))
        total_chats = (student_chats or 0) + (admission_chats or 0)

        # Tổng số embedding
        total_embeddings = await db.scalar(text("""
            SELECT 
                (SELECT COUNT(*) FROM embedding_admissions_20250709) +
                (SELECT COUNT(*) FROM embedding_students_20250709) +
                (SELECT COUNT(*) FROM embedding_pdfs_20250709)
        """))

        # Tổng số lượt truy trang
        total_page_views = await db.scalar(text("SELECT COUNT(*) FROM page_views"))

        # Phân bổ embedding
        admissions_count = await db.scalar(text("SELECT COUNT(*) FROM embedding_admissions_20250709"))
        students_count = await db.scalar(text("SELECT COUNT(*) FROM embedding_students_20250709"))
        pdfs_count = await db.scalar(text("SELECT COUNT(*) FROM embedding_pdfs_20250709"))

        # Lượt hỏi theo ngày
        daily_chat_stats = (await db.execute(text("""
            SELECT TO_CHAR(created_at::date, 'YYYY-MM-DD') AS date, COUNT(*) as count
            FROM chat_history
            GROUP BY date
            ORDER BY date
        """))).mappings().all()

        # Người dùng mới theo ngày
        user_signup_stats = (await db.execute(text("""
            SELECT TO_CHAR(created_at::date, 'YYYY-MM-DD') AS date, COUNT(*) as count
            FROM user_20250627
            GROUP BY date
            ORDER BY date
        """))).mappings().all()

        # Lượt truy cập theo ngày
        page_view_stats = (await db.execute(text("""
            SELECT TO_CHAR(viewed_at::date, 'YYYY-MM-DD') AS date, COUNT(*) as count
            FROM page_views
            GROUP BY date
            ORDER BY date
        """))).mappings().all()

        # Top 5 trang truy cập nhiều nhất
        top_pages = (await db.execute(text("""
            SELECT path, COUNT(*) as count
            FROM page_views
            GROUP BY path
            ORDER BY count DESC
            LIMIT 5
        """))).mappings().all()

        return {
            "total_users": total_users or 0,
            "total_chats": {
                "student": student_chats or 0,
                "admission": admission_chats or 0
            },
            "total_embeddings": total_embeddings or 0,
            "total_page_views": total_page_views or 0,
            "embedding_distribution": {
                "admissions": admissions_count or 0,
                "students": students_count or 0,
                "pdfs": pdfs_count or 0
            },
            "daily_chat_stats": daily_chat_stats,
            "user_signup_stats": user_signup_stats,
            "page_view_stats": page_view_stats,
            "top_pages": top_pages
        }

    except Exception as e:
        print("Lỗi khi thống kê:", e)
        return JSONResponse(status_code=500, content={"error": "Server error"})
