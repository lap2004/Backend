from fastapi import APIRouter, Request, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from datetime import datetime

router = APIRouter(tags=["Tracking"])

@router.post("/track")
async def track_page_view(request: Request, db: AsyncSession = Depends(get_db)):
    path = request.query_params.get("path") or request.url.path
    ip = request.client.host

    await db.execute(
        text("""
            INSERT INTO page_views (path, viewed_at)
            VALUES (:path, :viewed_at)
        """),
        {"path": path, "viewed_at": datetime.utcnow()}
    )
    await db.commit()
    return {"message": "view logged"}
