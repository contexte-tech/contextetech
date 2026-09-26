"""Profil public : publications d'un auteur et activité d'un membre."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Comment, Resource, User
from ..security import USERNAME_RE
from .resources import to_doc

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
async def labs(db: AsyncSession = Depends(get_db)):
    """Annuaire des Labs : comptes approuvés par l'administrateur pour publier des modèles."""
    nmod = (select(Resource.author_id, func.count().label("n"))
            .where(Resource.kind == "model", Resource.hidden.is_(False)).group_by(Resource.author_id).subquery())
    npub = (select(Resource.author_id, func.count().label("n"))
            .where(Resource.hidden.is_(False)).group_by(Resource.author_id).subquery())
    rows = (await db.execute(
        select(User, func.coalesce(nmod.c.n, 0), func.coalesce(npub.c.n, 0))
        .outerjoin(nmod, nmod.c.author_id == User.id).outerjoin(npub, npub.c.author_id == User.id)
        .where(User.is_lab.is_(True), User.hidden.is_(False)).order_by(func.coalesce(nmod.c.n, 0).desc(), User.username)
    )).all()
    return {"items": [{"name": u.username, "bio": u.bio, "city": u.city, "country": u.country, "website": u.website,
                       "models": m, "resources": p} for u, m, p in rows]}


@router.get("/{name}")
async def public_profile(name: str, db: AsyncSession = Depends(get_db)):
    name = name.strip().lower()
    if not USERNAME_RE.match(name):
        raise HTTPException(404, "not_found")
    user = (await db.execute(select(User).where(User.username == name))).scalar_one_or_none()
    rows = (await db.execute(
        select(Resource).where(Resource.author_handle == name, Resource.hidden.is_(False)).order_by(Resource.updated_at.desc()).limit(200)
    )).scalars().all()
    if (user is None and not rows) or (user is not None and user.hidden):
        raise HTTPException(404, "not_found")
    n_comments = 0
    if user is not None:
        n_comments = (await db.execute(select(func.count()).select_from(Comment).where(Comment.user_id == user.id))).scalar_one()
    return {
        "name": name, "member": user is not None, "isAdmin": bool(user and user.is_admin), "isLab": bool(user and user.is_lab),
        "createdAt": int(user.created_at.timestamp() * 1000) if user else 0,
        "bio": user.bio if user else "", "country": user.country if user else "", "city": user.city if user else "",
        "website": user.website if user else "",
        "resources": [to_doc(r, full=False) for r in rows], "comments": n_comments,
        "likes": sum(r.likes_count for r in rows), "uses": sum(r.uses for r in rows),
    }
