import uuid
from sqlalchemy import Boolean, Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base

class User(Base):
    __tablename__ = "user_20250627"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="student")
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # nên có để vô hiệu hóa tài khoản
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    force_password_change = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false")
    )
