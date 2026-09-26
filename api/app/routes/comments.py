"""Commentaires de la communauté : lecture publique, écriture pour tout compte connecté."""
import time

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Comment, Resource, User
from ..redis import redis
from ..security import current_user

router = APIRouter(prefix="/api", tags=["comments"])
MAX_LEN = 2000
PER_MINUTE = 5


def _safe(nxt: str) -> str:
    return nxt if nxt.startswith("/") and not nxt.startswith("//") else "/"


@router.get("/resources/{rid}/comments")
async def list_comments(rid: str, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(Comment, User.username).join(User, User.id == Comment.user_id)
        .where(Comment.resource_id == rid).order_by(Comment.created_at).limit(500)
    )).all()
    return {"items": [{"id": c.id, "author": name, "authorId": str(c.user_id), "body": c.body,
                       "createdAt": int(c.created_at.timestamp() * 1000)} for c, name in rows]}


# Formulaires HTML classiques (fonctionnent sans JavaScript) : on revient sur la fiche après l'action.
@router.post("/resources/{rid}/comments")
async def add_comment(rid: str, body: str = Form(...), next: str = Form("/"),
                      db: AsyncSession = Depends(get_db), user: User | None = Depends(current_user)):
    nxt = _safe(next)
    if user is None:
        return RedirectResponse(f"/a2/?next={nxt}", status_code=303)
    text = body.strip()[:MAX_LEN]
    if not text:
        return RedirectResponse(nxt + "#commentaires", status_code=303)
    if await db.get(Resource, rid) is None:
        raise HTTPException(404, "not_found")
    key = f"rate:comment:{user.id}:{int(time.time() // 60)}"
    n = await redis.incr(key)
    if n == 1:
        await redis.expire(key, 70)
    if n > PER_MINUTE:
        raise HTTPException(429, "rate_limited")
    db.add(Comment(resource_id=rid, user_id=user.id, body=text))
    await db.commit()
    return RedirectResponse(nxt + "#commentaires", status_code=303)


@router.post("/comments/{cid}/delete")
async def delete_comment(cid: int, next: str = Form("/"), db: AsyncSession = Depends(get_db),
                         user: User | None = Depends(current_user)):
    c = await db.get(Comment, cid)
    # L'auteur ou l'administrateur (modération)
    if c is not None and user is not None and (c.user_id == user.id or user.is_admin):
        await db.delete(c)
        await db.commit()
    return RedirectResponse(_safe(next) + "#commentaires", status_code=303)
