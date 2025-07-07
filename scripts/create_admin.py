import asyncio
import uuid
from sqlalchemy import select

from app.core.security import password  # dùng phiên bản plaintext
from app.db.database import AsyncSessionLocal
from app.db.models.user_model import User  # ✅ đúng tên

async def create_admin():
    async with AsyncSessionLocal() as session:
        admin_email = "admin@vanlanguni.vn"
        admin_password = "VLU@2025"
        admin_id = uuid.UUID("82aa81f6-48f5-498d-bf57-1809975deac7")

        # Kiểm tra trùng email
        result = await session.execute(select(User).where(User.email == admin_email))
        existing = result.scalar_one_or_none()
        if existing:
            print("❌ Admin đã tồn tại.")
            return

        # Tạo tài khoản admin
        user = User(
            id=admin_id,
            email=admin_email,
            full_name="Admin",
            role="admin",
            password=password(admin_password),  # plaintext
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        print("✅ Đã tạo tài khoản admin.")

if __name__ == "__main__":
    asyncio.run(create_admin())
