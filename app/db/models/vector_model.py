from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
import uuid

Base = declarative_base()

class BaseEmbeddingMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1024))  
    type = Column(Text)
    field = Column(Text)
    source = Column(Text)
    title_raw = Column(Text)
    ma_nganh = Column(String)
    doi_tuong = Column(String)
    chunk_index = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

class EmbeddingAdmissions(Base, BaseEmbeddingMixin):
    __tablename__ = "embedding_admissions_20250709"

class EmbeddingStudents(Base, BaseEmbeddingMixin):
    __tablename__ = "embedding_students_20250709"

class EmbeddingPDFs(Base):
    __tablename__ = "embedding_pdfs_20250709"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1024))
    type = Column(Text)
    field = Column(Text)
    source = Column(Text)
    title_raw = Column(Text)
    ma_nganh = Column(String)
    doi_tuong = Column(String)
    filename = Column(String)
    file_type = Column(String)
    page_number = Column(Integer)
    chunk_index = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
