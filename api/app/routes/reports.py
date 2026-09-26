"""Signalement d'une ressource ou d'un profil par un visiteur (formulaire HTML, sans JavaScript)."""
import hashlib
import time

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Report, User
from ..redis import redis
from ..security import current_user

router = APIRouter(prefix="/api", tags=["reports"])


@router.post("/report")
async def report(request: Request, target_type: str = Form(...), target_id: str = Form(...), reason: str = Form(""),
                 next: str = Form("/"), db: AsyncSession = Depends(get_db), user: User | None = Depends(current_user)):
    nxt = next if next.startswith("/") and not next.startswith("//") else "/"
    sep = "&" if "?" in nxt else "?"
    if target_type not in ("resource", "user") or not target_id or len(target_id) > 120:
        return RedirectResponse(nxt, status_code=303)
    # Un signalement par personne (compte ou IP) et par cible et par jour
    who = str(user.id) if user else hashlib.sha256((request.client.host if request.client else "?").encode()).hexdigest()[:16]
    key = f"report:{who}:{target_type}:{target_id}:{int(time.time() // 86400)}"
    if await redis.set(key, "1", ex=90000, nx=True):
        db.add(Report(target_type=target_type, target_id=target_id, reporter_id=user.id if user else None, reason=reason.strip()[:500]))
        await db.commit()
    return RedirectResponse(f"{nxt}{sep}signale=1", status_code=303)
