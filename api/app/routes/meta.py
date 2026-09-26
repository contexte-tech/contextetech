from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_db
from ..redis import redis

router = APIRouter(tags=["meta"])


@router.get("/api/config")
async def config():
    s = get_settings()
    return {"siteName": s.site_name, "sampleEnabled": s.llm_enabled,
            "objectStorage": s.s3_enabled, "maxResourceKb": s.max_resource_kb, "maxDatasetMb": s.max_dataset_mb}


@router.get("/healthz")
async def healthz(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    await redis.ping()
    return {"ok": True}
