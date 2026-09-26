"""Profil du membre connecté : activité, mot de passe, suppression du compte."""
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..models import Comment, Like, Resource, User
from ..security import COOKIE, close_session, current_user, hash_password, require_user, revoke_sessions, verify_password

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _ms(dt) -> int:
    return int(dt.timestamp() * 1000) if dt else 0


def _back(msg: str, tab: str) -> RedirectResponse:
    # Retour sur l'onglet du formulaire envoyé
    return RedirectResponse(f"/a2/profil?s={tab}&m={msg}", status_code=303)


@router.get("")
async def profile(db: AsyncSession = Depends(get_db), user: User = Depends(require_user)):
    comments = (await db.execute(
        select(Comment, Resource.name, Resource.author_handle, Resource.kind).join(Resource, Resource.id == Comment.resource_id)
        .where(Comment.user_id == user.id).order_by(Comment.created_at.desc()).limit(100)
    )).all()
    likes = (await db.execute(
        select(Resource.id, Resource.name, Resource.author_handle, Resource.kind).join(Like, Like.resource_id == Resource.id)
        .where(Like.user_id == user.id).order_by(Resource.name).limit(200)
    )).all()
    return {
        "name": user.username, "isAdmin": user.is_admin, "createdAt": _ms(user.created_at),
        "email": user.email or "", "bio": user.bio or "", "country": user.country or "", "city": user.city or "", "website": user.website or "",
        "isLab": bool(user.is_lab), "labRequest": user.lab_request or "", "labRequested": user.lab_requested_at is not None,
        "comments": [{"id": c.id, "resourceId": c.resource_id, "resource": f"{h or 'community'}/{n}", "kind": k, "body": c.body,
                      "createdAt": _ms(c.created_at)} for c, n, h, k in comments],
        "likes": [{"id": i, "resource": f"{h or 'community'}/{n}", "kind": k} for i, n, h, k in likes],
    }


# Formulaires HTML classiques : retour sur /a2/profil avec un message
@router.post("/info")
async def update_info(bio: str = Form(""), country: str = Form(""), city: str = Form(""), website: str = Form(""), email: str = Form(""),
                      db: AsyncSession = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return RedirectResponse("/a2/?next=/a2/profil", status_code=303)
    website = website.strip()
    if website and not re.match(r"^https?://[^\s<>\"]+$", website):
        return _back("url_bad", "profil")
    # Adresse e-mail : facultative ici (anciens comptes), mais valide et propre à un seul compte
    from .auth import clean_email, email_taken
    addr = clean_email(email) if email.strip() else ""
    if email.strip() and not addr:
        return _back("email", "profil")
    if addr and await email_taken(db, addr, user.id):
        return _back("email_taken", "profil")
    user.email = addr
    user.bio, user.country, user.city, user.website = bio.strip()[:500], country.strip()[:60], city.strip()[:80], website[:300]
    await db.commit()
    return _back("info_ok", "profil")


@router.post("/lab")
async def request_lab(motivation: str = Form(""), db: AsyncSession = Depends(get_db), user: User | None = Depends(current_user)):
    """Demande du statut Lab : l'administrateur l'approuve ou la refuse dans /a3/membres."""
    if user is None:
        return RedirectResponse("/a2/?next=/a2/profil?s=lab", status_code=303)
    if not user.is_lab:
        user.lab_request = motivation.strip()[:500]
        user.lab_requested_at = datetime.now(timezone.utc)
        await db.commit()
    return _back("lab_sent", "lab")


@router.post("/password")
async def change_password(request: Request, old: str = Form(...), new: str = Form(...), new2: str = Form(...),
                          db: AsyncSession = Depends(get_db), user: User | None = Depends(current_user)):
    if user is None:
        return RedirectResponse("/a2/?next=/a2/profil", status_code=303)
    if not verify_password(user.password_hash, old):
        return _back("pw_wrong", "securite")
    if len(new) < 10:
        return _back("password_short", "securite")
    if new != new2:
        return _back("password_mismatch", "securite")
    user.password_hash = hash_password(new)
    await db.commit()
    await revoke_sessions(user.id, keep=request.cookies.get(COOKIE))
    return _back("pw_ok", "securite")


@router.post("/delete")
async def delete_account(request: Request, password: str = Form(...), db: AsyncSession = Depends(get_db),
                         user: User | None = Depends(current_user)):
    # Droit à l'effacement : le compte, ses commentaires et ses likes disparaissent (cascade)
    if user is None:
        return RedirectResponse("/a2/", status_code=303)
    if user.is_admin:
        return _back("admin_keep", "compte")
    if not verify_password(user.password_hash, password):
        return _back("pw_wrong", "compte")
    # Les compteurs de likes des ressources restent justes
    liked = (await db.execute(select(Like.resource_id).where(Like.user_id == user.id))).scalars().all()
    for rid in liked:
        r = await db.get(Resource, rid)
        if r is not None:
            r.likes_count = max(0, r.likes_count - 1)
    await revoke_sessions(user.id)
    await db.execute(delete(User).where(User.id == user.id))
    await db.commit()
    resp = RedirectResponse("/", status_code=303)
    await close_session(request, resp)
    return resp
