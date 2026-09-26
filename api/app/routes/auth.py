import hashlib
import re
import secrets
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Depends, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db import get_db
from ..mail_texts import mail
from ..mailer import send_mail
from ..models import User
from ..redis import redis
from ..security import (
    USERNAME_RE, close_session, current_user, hash_password, open_session, revoke_sessions, too_many, user_json, verify_password,
)

EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$")
RESET_TTL = 3600                          # lien de réinitialisation valable 1 heure


def clean_email(v: str) -> str:
    v = v.strip().lower()[:254]
    return v if EMAIL_RE.match(v) else ""


async def email_taken(db: AsyncSession, email: str, except_id: int | None = None) -> bool:
    q = select(User.id).where(func.lower(User.email) == email)
    if except_id is not None:
        q = q.where(User.id != except_id)
    return (await db.execute(q)).first() is not None

router = APIRouter(prefix="/api/auth", tags=["auth"])
LANGS = {"fr", "en", "es", "de", "it"}
# Segments d'adresse du site : interdits comme identifiants
RESERVED = {"tag", "admin", "api", "a2", "a3", "profil", "profile", "perfil", "profilo", "page", "pagina", "seite",
            "langue", "language", "idioma", "sprache", "lingua", "tri", "sort", "orden", "sortierung", "ordine",
            "few-shot", "persona", "chat", "instruction", "completion", "lora", "qlora", "fonction", "function",
            "funcion", "funktion", "funzione", "fine-tune", "merge", "base", "quantifie", "quantized", "cuantizado", "quantisiert", "quantizzato", "modeles", "models", "labs", "lab", "mcp", "outils", "tools", "contextes", "contexts", "docs", "agents", "skills", "evaluations", "evals", "rag", "harness", "usage", "entrainement", "training", "extensions", "modele", "model", "modelo", "modell", "modello", "connaissances", "knowledge", "wissen", "conoscenze", "conocimiento"}


def _home(lang: str) -> str:
    # Le français vit à la racine, les autres langues sous /en/, /es/…
    return "/" if lang == "fr" else f"/{lang}/"


def _safe_next(nxt: str, lang: str) -> str:
    return nxt if nxt.startswith("/") and not nxt.startswith("//") else _home(lang)


def _back(error: str, nxt: str, page: str = "") -> RedirectResponse:
    return RedirectResponse(f"/a2/{page}?error={error}&next={quote(nxt)}", status_code=303)


@router.get("/me")
async def me(user: User | None = Depends(current_user)):
    return user_json(user)


@router.post("/login")
async def login(
    request: Request, background: BackgroundTasks, username: str = Form(...), password: str = Form(...),
    lang: str = Form("fr"), next: str = Form("/"),
    db: AsyncSession = Depends(get_db),
):
    lang = lang if lang in LANGS else "fr"
    nxt = _safe_next(next, lang)
    name = username.strip().lower()[:30]
    ip = request.client.host if request.client else "?"
    # Force brute : 20 essais par IP et 8 échecs par identifiant sur 15 minutes
    if await too_many(f"rate:login:ip:{ip}", 20, 900) or int(await redis.get(f"rate:login:fail:{name}") or 0) >= 8:
        return _back("too_many", nxt)
    # Identifiant ou adresse e-mail
    by = func.lower(User.email) == name if "@" in name else User.username == name
    user = (await db.execute(select(User).where(by))).scalar_one_or_none()
    if user is None or not verify_password(user.password_hash, password):
        await too_many(f"rate:login:fail:{name}", 10**6, 900)
        return _back("invalid", nxt)
    await redis.delete(f"rate:login:fail:{name}")
    resp = RedirectResponse(nxt, status_code=303)
    await open_session(resp, user.id)
    if user.email:
        s = get_settings()
        subject, text, html = mail("login", lang, site=s.site_name, origin=s.public_origin, user=user.username, ip=ip,
                                   agent=(request.headers.get("user-agent") or "?")[:200])
        background.add_task(send_mail, user.email, subject, text, True, html)
    return resp


@router.post("/signup")
async def signup(
    request: Request, background: BackgroundTasks, username: str = Form(...), email: str = Form(""),
    password: str = Form(...), password2: str = Form(...),
    accept: str = Form(""), lang: str = Form("fr"), next: str = Form("/"),
    db: AsyncSession = Depends(get_db),
):
    # Comptes de la communauté : ils commentent et aiment ; publier reste réservé à l'administrateur
    lang = lang if lang in LANGS else "fr"
    nxt = _safe_next(next, lang)
    # 5 comptes par IP et par heure
    if await too_many(f"rate:signup:{request.client.host if request.client else '?'}", 5, 3600):
        return _back("too_many", nxt, "inscription")
    name = username.strip().lower()
    if not USERNAME_RE.match(name) or name in RESERVED:
        return _back("username", nxt, "inscription")
    mail_addr = clean_email(email)
    if not mail_addr:
        return _back("email", nxt, "inscription")
    if len(password) < 10:
        return _back("password_short", nxt, "inscription")
    if password != password2:
        return _back("password_mismatch", nxt, "inscription")
    if accept != "1":
        return _back("accept", nxt, "inscription")
    if (await db.execute(select(User.id).where(User.username == name))).first():
        return _back("taken", nxt, "inscription")
    if await email_taken(db, mail_addr):
        return _back("email_taken", nxt, "inscription")
    user = User(username=name, email=mail_addr, password_hash=hash_password(password))
    db.add(user)
    await db.commit()
    resp = RedirectResponse(nxt, status_code=303)
    await open_session(resp, user.id)
    s = get_settings()
    subject, text, html = mail("welcome", lang, site=s.site_name, origin=s.public_origin, user=name, email=mail_addr)
    background.add_task(send_mail, mail_addr, subject, text, True, html)
    return resp


@router.post("/forgot")
async def forgot(request: Request, background: BackgroundTasks, email: str = Form(""), lang: str = Form("fr"),
                 db: AsyncSession = Depends(get_db)):
    """Mot de passe oublié : lien par e-mail. Même réponse que l'adresse existe ou non (pas d'énumération)."""
    lang = lang if lang in LANGS else "fr"
    ip = request.client.host if request.client else "?"
    addr = clean_email(email)
    if addr and not await too_many(f"rate:forgot:ip:{ip}", 5, 900) and not await too_many(f"rate:forgot:mail:{addr}", 3, 3600):
        user = (await db.execute(select(User).where(func.lower(User.email) == addr))).scalar_one_or_none()
        if user:
            token = secrets.token_urlsafe(32)
            await redis.set(f"reset:{hashlib.sha256(token.encode()).hexdigest()}", str(user.id), ex=RESET_TTL)
            s = get_settings()
            subject, text, html = mail("reset", lang, site=s.site_name, origin=s.public_origin, user=user.username,
                                       link=f"{s.public_origin}/a2/reinitialiser?token={token}")
            background.add_task(send_mail, user.email, subject, text, False, html)   # jamais en copie : le lien donne accès au compte
    return RedirectResponse("/a2/mot-de-passe-oublie?sent=1", status_code=303)


@router.post("/reset")
async def reset(token: str = Form(""), password: str = Form(...), password2: str = Form(...), db: AsyncSession = Depends(get_db)):
    """Nouveau mot de passe depuis le lien reçu : lien à usage unique, toutes les sessions ouvertes sont fermées."""
    back = lambda e: RedirectResponse(f"/a2/reinitialiser?token={quote(token)}&error={e}", status_code=303)
    if len(password) < 10:
        return back("password_short")
    if password != password2:
        return back("password_mismatch")
    key = f"reset:{hashlib.sha256(token.encode()).hexdigest()}"
    uid = await redis.getdel(key) if token else None
    user = await db.get(User, int(uid)) if uid else None
    if user is None:
        return RedirectResponse("/a2/mot-de-passe-oublie?error=reset_invalid", status_code=303)
    user.password_hash = hash_password(password)
    await db.commit()
    await revoke_sessions(user.id)
    resp = RedirectResponse("/a2/?reset=ok", status_code=303)
    await open_session(resp, user.id)
    return resp


@router.post("/logout")
async def logout(request: Request, lang: str = Form("fr")):
    resp = RedirectResponse(_home(lang if lang in LANGS else "fr"), status_code=303)
    await close_session(request, resp)
    return resp


@router.post("/logout.json")
async def logout_json(request: Request):
    resp = JSONResponse({"ok": True})
    await close_session(request, resp)
    return resp
