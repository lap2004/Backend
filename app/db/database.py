from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
from sqlalchemy import create_engine

Base = declarative_base()

sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=False 
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

def get_sync_session():
    """
    Dùng trong script như embed_runner.py
    """
    return SessionLocal()

async_engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=False 
)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
