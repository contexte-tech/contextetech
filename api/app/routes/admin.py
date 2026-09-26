"""Outils de l'administrateur : modération des ressources publiées par les membres."""
import re

from fastapi import APIRouter, Depends, Form, HTTPException, Query
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..alerts import resource_alert, user_alert
from ..models import Comment, Report, Resource, User
from ..redis import bump_cache
from ..security import current_user, require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _ms(dt) -> int:
    return int(dt.timestamp() * 1000) if dt else 0


async def _reports(db, target_type):
    return dict((await db.execute(select(Report.target_id, func.count()).where(Report.target_type == target_type)
                                  .group_by(Report.target_id))).all())


@router.get("/resources")
async def moderation_list(status: str = Query("all", pattern="^(all|visible|hidden)$"), q: str = Query("", max_length=80),
                          min: int = Query(0, ge=0, le=5), db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    ncom = select(Comment.resource_id, func.count().label("n")).group_by(Comment.resource_id).subquery()
    stmt = (select(Resource, User, func.coalesce(ncom.c.n, 0))
            .outerjoin(User, User.id == Resource.author_id).outerjoin(ncom, ncom.c.resource_id == Resource.id))
    if status != "all":
        stmt = stmt.where(Resource.hidden.is_(status == "hidden"))
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(Resource.name.ilike(like) | Resource.author_handle.ilike(like))
    rows = (await db.execute(stmt.order_by(Resource.created_at.desc()).limit(300))).all()
    counts = dict((await db.execute(select(Resource.hidden, func.count()).group_by(Resource.hidden))).all())
    # Données des critères d'alerte
    reports = await _reports(db, "resource")
    pubs = dict((await db.execute(select(Resource.author_id, func.count()).group_by(Resource.author_id))).all())
    hour = datetime.now(timezone.utc) - timedelta(hours=1)
    recent = dict((await db.execute(select(Resource.author_id, func.count()).where(Resource.created_at > hour)
                                    .group_by(Resource.author_id))).all())
    names = dict((await db.execute(select(Resource.name, func.count()).group_by(Resource.name))).all())
    items = []
    for r, author, n in rows:
        level, why = resource_alert(r, author, reports.get(r.id, 0), pubs.get(r.author_id, 0),
                                    recent.get(r.author_id, 0), names.get(r.name, 0) > 1)
        if level >= min:
            items.append({"id": r.id, "kind": r.kind, "name": r.name, "author": r.author_handle or (author.username if author else ""),
                          "hidden": r.hidden, "likes": r.likes_count, "uses": r.uses, "comments": n,
                          "createdAt": _ms(r.created_at), "alert": level, "why": why, "reports": reports.get(r.id, 0)})
    return {"counts": {"visible": counts.get(False, 0), "hidden": counts.get(True, 0),
                       "alerts": sum(1 for i in items if i["alert"] >= 3 and not i["hidden"])},
            "items": items}


@router.get("/users")
async def members(status: str = Query("all", pattern="^(all|visible|hidden|lab)$"), q: str = Query("", max_length=80),
                  min: int = Query(0, ge=0, le=5), db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    npub = select(Resource.author_id, func.count().label("n")).group_by(Resource.author_id).subquery()
    ncom = select(Comment.user_id, func.count().label("n")).group_by(Comment.user_id).subquery()
    stmt = (select(User, func.coalesce(npub.c.n, 0), func.coalesce(ncom.c.n, 0))
            .outerjoin(npub, npub.c.author_id == User.id).outerjoin(ncom, ncom.c.user_id == User.id))
    if status in ("visible", "hidden"):
        stmt = stmt.where(User.hidden.is_(status == "hidden"))
    if q.strip():
        stmt = stmt.where(User.username.ilike(f"%{q.strip()}%"))
    if status == "lab":
        stmt = stmt.where(User.lab_requested_at.is_not(None), User.is_lab.is_(False))
    rows = (await db.execute(stmt.order_by(User.created_at.desc()).limit(300))).all()
    counts = dict((await db.execute(select(User.hidden, func.count()).group_by(User.hidden))).all())
    lab_pending = (await db.execute(select(func.count()).select_from(User)
                                    .where(User.lab_requested_at.is_not(None), User.is_lab.is_(False)))).scalar_one()
    reports = await _reports(db, "user")
    hour = datetime.now(timezone.utc) - timedelta(hours=1)
    recent = dict((await db.execute(select(Comment.user_id, func.count()).where(Comment.created_at > hour)
                                    .group_by(Comment.user_id))).all())
    items = []
    for u, p, c in rows:
        level, why = user_alert(u, reports.get(u.username, 0), recent.get(u.id, 0))
        if level >= min:
            items.append({"name": u.username, "isAdmin": u.is_admin, "hidden": u.hidden, "isLab": bool(u.is_lab),
                          "labRequest": u.lab_request or "", "labRequested": u.lab_requested_at is not None, "bio": u.bio, "website": u.website,
                          "createdAt": _ms(u.created_at), "resources": p, "comments": c, "alert": level, "why": why,
                          "reports": reports.get(u.username, 0)})
    return {"counts": {"visible": counts.get(False, 0), "hidden": counts.get(True, 0), "lab": lab_pending,
                       "alerts": sum(1 for i in items if i["alert"] >= 3 and not i["hidden"])},
            "items": items}


@router.post("/users/{name}/lab")
async def set_lab(name: str, action: str = Form(...), next: str = Form("/a3/membres"),
                  db: AsyncSession = Depends(get_db), user: User | None = Depends(current_user)):
    """approve : accorde le statut Lab ; refuse : rejette la demande ; revoke : retire le statut."""
    if user is None or not user.is_admin:
        raise HTTPException(403, "forbidden")
    target = (await db.execute(select(User).where(User.username == name))).scalar_one_or_none()
    if target is None:
        raise HTTPException(404, "not_found")
    if action == "approve":
        target.is_lab = True
    elif action in ("refuse", "revoke"):
        target.is_lab = False
        target.lab_requested_at = None
    await db.commit()
    nxt = next if next.startswith("/") and not next.startswith("//") else "/a3/membres"
    return RedirectResponse(nxt, status_code=303)


@router.post("/users/{name}/visibility")
async def set_user_visibility(name: str, hidden: str = Form(...), next: str = Form("/a3/membres"),
                              db: AsyncSession = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None or not user.is_admin:
        raise HTTPException(403, "forbidden")
    target = (await db.execute(select(User).where(User.username == name))).scalar_one_or_none()
    if target is None:
        raise HTTPException(404, "not_found")
    if not target.is_admin:
        target.hidden = hidden == "1"
        await db.commit()
        await bump_cache()
    nxt = next if next.startswith("/") and not next.startswith("//") else "/a3/membres"
    return RedirectResponse(nxt, status_code=303)


@router.get("/tags")
async def all_tags(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    tag = func.unnest(Resource.tags).label("tag")
    sub = select(tag).subquery()
    rows = (await db.execute(select(sub.c.tag, func.count()).group_by(sub.c.tag).order_by(func.count().desc(), sub.c.tag))).all()
    return {"items": [[t, n] for t, n in rows]}


# Renommer un tag partout ; si le nouveau existe déjà sur une ressource, les deux fusionnent
@router.post("/tags/rename")
async def rename_tag(old: str = Form(...), new: str = Form(""), db: AsyncSession = Depends(get_db),
                     user: User | None = Depends(current_user)):
    if user is None or not user.is_admin:
        raise HTTPException(403, "forbidden")
    old, new = old.strip().lower(), re.sub(r"[^a-z0-9._-]+", "-", new.strip().lower()).strip("-")[:40]
    rows = (await db.execute(select(Resource).where(Resource.tags.any(old)))).scalars().all()
    for r in rows:
        tags = [new if t == old else t for t in r.tags if new or t != old]
        r.tags = list(dict.fromkeys(t for t in tags if t))
    await db.commit()
    await bump_cache()
    return RedirectResponse(f"/a3/tags?m={len(rows)}", status_code=303)


# Formulaire HTML : désapprouver (masquer) ou réapprouver, puis retour à la page de modération
@router.post("/resources/{rid}/visibility")
async def set_visibility(rid: str, hidden: str = Form(...), next: str = Form("/a3/"),
                         db: AsyncSession = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None or not user.is_admin:
        raise HTTPException(403, "forbidden")
    r = await db.get(Resource, rid)
    if r is None:
        raise HTTPException(404, "not_found")
    r.hidden = hidden == "1"
    await db.commit()
    await bump_cache()
    nxt = next if next.startswith("/") and not next.startswith("//") else "/a3/"
    return RedirectResponse(nxt, status_code=303)
