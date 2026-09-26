"""Niveau d'alerte de modération, de 1 (info) à 5 (critique). Le niveau retenu est le plus haut des critères déclenchés.

1 Info        rien d'anormal, à noter
2 À vérifier  nouveau ou inhabituel
3 Suspect     probablement un problème
4 Grave       problème quasi certain ou risque pour les utilisateurs
5 Critique    spam ou abus évident
"""
import json
import re
from datetime import datetime, timedelta, timezone

URL_RE = re.compile(r"https?://|www\.", re.I)
SPAM_RE = re.compile(r"\b(casino|viagra|cialis|porn|xxx|escort|crypto ?(?:pump|signal)|forex|bitcoin doubler|loan|pr[eê]t rapide|seo backlinks?)\b", re.I)
SECRET_RE = re.compile(r"(sk-ant-[a-z0-9_-]{10,}|sk-[a-z0-9]{20,}|ghp_[a-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[bp]-[a-z0-9-]{10,}|"
                       r"\"?(?:password|passwd|api[_-]?key|secret|token)\"?\s*[:=]\s*\"?[^\s\",]{6,})", re.I)


def _level(hits):
    return max((lvl for lvl, _ in hits), default=0), [why for _, why in sorted(hits, reverse=True)]


def _caps(text):
    letters = [c for c in text if c.isalpha()]
    return len(letters) > 20 and sum(c.isupper() for c in letters) / len(letters) > 0.7


def _new(dt, hours=24):
    return dt is not None and datetime.now(timezone.utc) - dt < timedelta(hours=hours)


def resource_alert(r, author, n_reports, author_pubs, author_recent, dup):
    hits = []
    text = f"{r.name} {r.description} {' '.join(r.tags or [])}"
    body = json.dumps(r.data or {}, ensure_ascii=False)
    if SPAM_RE.search(text + " " + body):
        hits.append((5, "mots de spam"))
    if n_reports >= 3:
        hits.append((5, f"{n_reports} signalements"))
    elif n_reports:
        hits.append((3, f"{n_reports} signalement(s)"))
    if len(URL_RE.findall(r.description or "")) >= 2:
        hits.append((4, "plusieurs liens dans la description"))
    if SECRET_RE.search(body):
        hits.append((4, "clé API ou mot de passe dans le contenu"))
    if author_recent >= 5:
        hits.append((3, f"{author_recent} publications en 1 h"))
    if dup:
        hits.append((3, "doublon d'une autre ressource"))
    if _caps(r.description or ""):
        hits.append((3, "texte en majuscules"))
    if author is not None and not author.is_admin:
        if _new(author.created_at):
            hits.append((2, "compte de moins de 24 h"))
        if author_pubs == 1:
            hits.append((2, "première publication du membre"))
    if not r.description:
        hits.append((1, "pas de description"))
    if not r.tags:
        hits.append((1, "aucun tag"))
    if len(body) < 40:
        hits.append((1, "contenu très court"))
    return _level(hits)


def user_alert(u, n_reports, recent_comments):
    hits = []
    text = f"{u.bio} {u.website}"
    if u.is_admin:
        return 0, []
    if SPAM_RE.search(text):
        hits.append((5, "mots de spam"))
    if n_reports >= 3:
        hits.append((5, f"{n_reports} signalements"))
    elif n_reports:
        hits.append((3, f"{n_reports} signalement(s)"))
    if len(URL_RE.findall(u.bio or "")) >= 2:
        hits.append((4, "plusieurs liens dans la présentation"))
    if u.website and _new(u.created_at):
        hits.append((4, "site web sur un compte tout neuf"))
    if recent_comments >= 10:
        hits.append((3, f"{recent_comments} commentaires en 1 h"))
    if _caps(u.bio or ""):
        hits.append((3, "texte en majuscules"))
    if _new(u.created_at):
        hits.append((2, "compte de moins de 24 h"))
    if URL_RE.search(u.bio or ""):
        hits.append((2, "lien dans la présentation"))
    return _level(hits)
