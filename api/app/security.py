import re
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .db import get_db
from .models import User
from .redis import redis

COOKIE = "ctx_session"
USERNAME_RE = re.compile(r"^[a-z0-9_-]{3,30}$")
_ph = PasswordHasher()


def hash_password(pw: str) -> str:
    return _ph.hash(pw)


def verify_password(h: str, pw: str) -> bool:
    try:
        return _ph.verify(h, pw)
    except (VerificationError, InvalidHashError):
        return False


async def open_session(response: Response, user_id: int) -> None:
    s = get_settings()
    token = secrets.token_urlsafe(32)
    ttl = s.session_days * 86400
    await redis.set(f"session:{token}", str(user_id), ex=ttl)
    await redis.sadd(f"sessions:{user_id}", token)
    await redis.expire(f"sessions:{user_id}", ttl)
    response.set_cookie(COOKIE, token, max_age=ttl, httponly=True, secure=s.cookie_secure, samesite="lax", path="/")


async def close_session(request: Request, response: Response) -> None:
    token = request.cookies.get(COOKIE)
    if token:
        uid = await redis.get(f"session:{token}")
        await redis.delete(f"session:{token}")
        if uid:
            await redis.srem(f"sessions:{uid}", token)
    response.delete_cookie(COOKIE, path="/")


async def revoke_sessions(user_id: int, keep: str | None = None) -> None:
    """Déconnecte toutes les sessions d'un compte (sauf `keep`) : changement de mot de passe, suppression…"""
    for token in await redis.smembers(f"sessions:{user_id}"):
        token = token.decode() if isinstance(token, bytes) else token
        if token != keep:
            await redis.delete(f"session:{token}")
            await redis.srem(f"sessions:{user_id}", token)


async def too_many(key: str, limit: int, window: int) -> bool:
    """Compteur Redis à fenêtre fixe : vrai si `limit` est dépassé sur `window` secondes."""
    n = await redis.incr(key)
    if n == 1:
        await redis.expire(key, window)
    return n > limit


async def current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User | None:
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    uid = await redis.get(f"session:{token}")
    if not uid:
        return None
    return await db.get(User, int(uid))


async def require_user(user: User | None = Depends(current_user)) -> User:
    if user is None:
        raise HTTPException(401, "auth_required")
    return user


async def require_admin(user: User = Depends(require_user)) -> User:
    if not user.is_admin:
        raise HTTPException(403, "forbidden")
    return user


def user_json(u: User | None) -> dict:
    if u is None:
        return {"authenticated": False, "id": None, "name": "", "isAdmin": False, "isLab": False}
    return {"authenticated": True, "id": str(u.id), "name": u.username, "isAdmin": u.is_admin, "isLab": bool(u.is_lab)}
