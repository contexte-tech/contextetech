import json
import os
import re
import tempfile
import time

from fastapi import BackgroundTasks, APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse, RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .. import storage
from ..config import get_settings
from ..mail_texts import mail
from ..mailer import send_mail
from ..db import get_db
from ..formats import DatasetError, scan_jsonl, vars_of
from ..models import KINDS, SUB_FIELD, SUBS, Like, Resource, User
from ..redis import bump_cache, cache_version, redis
from ..security import current_user, require_user

router = APIRouter(prefix="/api", tags=["resources"])

ID_RE = re.compile(r"^[a-z0-9._-]{1,120}$")
NAME_RE = re.compile(r"^[a-z0-9._-]{1,60}$")
TAG_RE = re.compile(r"^[a-z0-9._-]{1,40}$")
CLANGS = {"fr", "en", "es", "de", "it", "pt", "nl", "multi", ""}
LICENSES = {"", "MIT", "Apache-2.0", "CC-BY-4.0", "CC-BY-SA-4.0", "CC-BY-NC-4.0", "CC0-1.0", "proprietary"}
PAGE_SIZE = 24
MODEL_FORMATS = ("safetensors", "gguf", "gptq", "awq", "mlx", "onnx")
# Modèle cible des contextes, prompts et outils : "" = général (tous modèles)
TARGET_FAMILIES = ("claude", "gpt", "gemini", "llama", "mistral", "qwen", "deepseek", "gemma", "phi", "other")
TARGET_KINDS = ("context", "prompt", "tool", "agent", "skill", "eval", "rag", "harness")
VECTOR_STORES = ("pgvector", "qdrant", "chroma", "weaviate", "pinecone", "faiss", "other")
HARNESSES = ("claude-code", "claude-agent-sdk", "cursor", "other")
AGENT_FRAMEWORKS = ("claude-agent-sdk", "langgraph", "crewai", "openai-agents", "other")
EVAL_METRICS = ("contains", "exact", "regex", "llm-judge")
CHAT_TEMPLATES = ("chatml", "llama3", "mistral", "gemma", "phi", "alpaca", "other")
MODEL_FAMILIES = ("llama", "mistral", "qwen", "gemma", "deepseek", "phi", "other")
PUBLISH_PER_DAY = 20                     # nouvelles ressources par membre et par jour
TOOL_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def _ms(dt) -> int:
    return int(dt.timestamp() * 1000) if dt else 0


def to_doc(r: Resource, author_name: str = "", liked: bool = False, full: bool = True) -> dict:
    doc = {
        "id": r.id, "kind": r.kind, "name": r.name,
        "authorId": str(r.author_id) if r.author_id else None,
        "authorHandle": r.author_handle or author_name or "",
        "description": r.description, "tags": r.tags or [], "clang": r.clang, "license": r.license, "sourceUrl": r.source_url or "", "hidden": bool(r.hidden),
        "uses": r.uses, "likes": r.likes_count, "liked": liked,
        "rowCount": r.row_count, "stored": "object" if r.blob_key else "inline",
        "createdAt": _ms(r.created_at), "updatedAt": _ms(r.updated_at),
    }
    if r.kind in SUB_FIELD:
        doc[SUB_FIELD[r.kind]] = r.sub
    data = r.data or {}
    tests = data.get("tests") or []
    if tests:
        doc["testsCount"], doc["testsPass"] = len(tests), sum(1 for x in tests if x.get("result") == "pass")
    if full:
        doc.update(data)
    else:
        # Champs légers pour les cartes du hub
        doc["targetFamily"] = data.get("targetFamily", "")
        if r.kind == "context":
            doc["examplesCount"] = len(data.get("examples") or [])
        elif r.kind == "prompt":
            doc["varsCount"] = len(vars_of(data.get("template", "")))
        elif r.kind == "tool":
            doc["toolName"] = data.get("toolName", "")
            doc["transport"] = data.get("transport", "")
        elif r.kind == "lora":
            doc["baseModel"] = data.get("baseModel", "")
            doc["r"] = data.get("r")
        elif r.kind == "agent":
            doc["stepsCount"] = len(data.get("steps") or [])
            doc["framework"] = data.get("framework", "")
        elif r.kind == "skill":
            doc["skillName"] = data.get("skillName", "")
        elif r.kind == "eval":
            doc["casesCount"] = len(data.get("cases") or [])
        elif r.kind == "rag":
            doc["vectorStore"] = data.get("vectorStore", "")
        elif r.kind == "harness":
            doc["harness"] = data.get("harness", "")
        elif r.kind == "model":
            doc["params"] = data.get("params", "")
            doc["format"] = data.get("format", "")
    return doc


# ---------- Lecture ----------

@router.get("/resources")
async def list_resources(
    kind: str = "context", sub: str = "", tag: str = "", clang: str = "", target: str = "", q: str = "",
    sort: str = Query("likes", pattern="^(likes|uses|recent)$"), page: int = Query(1, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    kinds_sel = [k for k in kind.split(",") if k in KINDS]
    if not kinds_sel and kind != "all":
        raise HTTPException(400, "invalid_kind")
    key = f"cache:{await cache_version()}:list:{kind}:{sub}:{tag}:{clang}:{target}:{q.lower()}:{sort}:{page}"
    if cached := await redis.get(key):
        return json.loads(cached)

    # "all" : toutes les ressources, tous types confondus (accueil)
    # "all" : tous types (accueil) ; "context,prompt" : une famille
    conds = [Resource.hidden.is_(False)] + ([] if kind == "all" else [Resource.kind.in_(kinds_sel)])
    if sub:
        conds.append(Resource.sub == sub)
    if tag:
        conds.append(Resource.tags.any(tag))
    if clang:
        conds.append(Resource.clang == clang)
    if target in TARGET_FAMILIES:
        conds.append(Resource.data["targetFamily"].astext == target)
    if q.strip():
        like = f"%{q.strip()[:80]}%"
        conds.append(or_(Resource.name.ilike(like), Resource.description.ilike(like),
                         Resource.author_handle.ilike(like), func.array_to_string(Resource.tags, " ").ilike(like)))
    order = {"likes": Resource.likes_count.desc(), "uses": Resource.uses.desc(),
             "recent": Resource.updated_at.desc()}[sort]
    where = and_(*conds)
    total = (await db.execute(select(func.count()).select_from(Resource).where(where))).scalar_one()
    rows = (await db.execute(
        select(Resource, User.username).outerjoin(User, User.id == Resource.author_id)
        .where(where).order_by(order, Resource.updated_at.desc())
        .limit(PAGE_SIZE).offset((page - 1) * PAGE_SIZE)
    )).all()
    out = {"items": [to_doc(r, name or "", full=False) for r, name in rows],
           "total": total, "page": page, "pageSize": PAGE_SIZE}
    await redis.set(key, json.dumps(out), ex=30)
    return out


@router.get("/facets")
async def facets(kind: str = "context", db: AsyncSession = Depends(get_db)):
    if kind not in KINDS and kind != "all":
        raise HTTPException(400, "invalid_kind")
    key = f"cache:{await cache_version()}:facets:{kind}"
    if cached := await redis.get(key):
        return json.loads(cached)
    kinds = dict((await db.execute(select(Resource.kind, func.count()).where(Resource.hidden.is_(False)).group_by(Resource.kind))).all())
    subs = dict((await db.execute(
        select(Resource.sub, func.count()).where(Resource.kind == kind, Resource.hidden.is_(False)).group_by(Resource.sub))).all())
    fsub = (select(Resource.data["targetFamily"].astext.label("fam"))
            .where(Resource.kind == kind, Resource.hidden.is_(False)).subquery())
    targets = dict((await db.execute(
        select(fsub.c.fam, func.count()).where(fsub.c.fam.in_(TARGET_FAMILIES)).group_by(fsub.c.fam))).all())
    clangs = dict((await db.execute(
        select(Resource.clang, func.count())
        .where(*([] if kind == "all" else [Resource.kind == kind]), Resource.clang != "", Resource.hidden.is_(False))
        .group_by(Resource.clang))).all())
    tag = func.unnest(Resource.tags).label("tag")
    tsub = select(tag).where(Resource.kind == kind, Resource.hidden.is_(False)).subquery()
    tags = (await db.execute(
        select(tsub.c.tag, func.count()).group_by(tsub.c.tag).order_by(func.count().desc()).limit(15))).all()
    out = {"kinds": {k: kinds.get(k, 0) for k in KINDS}, "subs": subs, "clangs": clangs, "targets": targets,
           "tags": [[t, n] for t, n in tags]}
    await redis.set(key, json.dumps(out), ex=30)
    return out


# Adresse publique d'une fiche (même règle que web/src/lib/paths.js) et libellés, pour les e-mails
DETAIL_SLUGS_FR = {"context": "contextes", "prompt": "prompts", "dataset": "datasets", "lora": "lora", "tool": "serveurs-mcp",
                   "model": "modeles", "agent": "agents", "skill": "skills", "eval": "evaluations", "rag": "rag", "harness": "harness"}
KIND_LABELS_FR = {"context": "Contexte", "prompt": "Prompt", "dataset": "Dataset", "lora": "LoRA", "tool": "Serveur MCP",
                  "model": "Modèle", "agent": "Agent", "skill": "Skill", "eval": "Évaluation", "rag": "Pipeline RAG", "harness": "Harness"}


def short_id(rid: str) -> str:
    """Identifiant court d'une fiche dans son adresse (/<type>/<nom>-<court>) : FNV-1a 32 bits en base 36.
    Même calcul côté site (web/src/lib/paths.js)."""
    h = 0x811C9DC5
    for b in rid.encode():
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    out, digits = "", "0123456789abcdefghijklmnopqrstuvwxyz"
    while True:
        h, r = divmod(h, 36)
        out = digits[r] + out
        if not h:
            return out


@router.get("/resources/by-slug/{kind}/{slug}", include_in_schema=False)
async def get_resource_by_slug(kind: str, slug: str, db: AsyncSession = Depends(get_db), user: User | None = Depends(current_user)):
    """Fiche d'après son adresse publique /<type>/<nom>-<court>."""
    name, _, short = slug.rpartition("-")
    ids = (await db.execute(select(Resource.id).where(Resource.kind == kind, Resource.name == name))).scalars().all()
    rid = next((i for i in ids if short_id(i) == short), None)
    if not rid:
        raise HTTPException(404, "not_found")
    return await get_resource(rid, db, user)


@router.get("/resources/{rid}")
async def get_resource(rid: str, db: AsyncSession = Depends(get_db), user: User | None = Depends(current_user)):
    row = (await db.execute(
        select(Resource, User.username).outerjoin(User, User.id == Resource.author_id).where(Resource.id == rid)
    )).first()
    if not row:
        raise HTTPException(404, "not_found")
    r, name = row
    # Ressource désapprouvée : 404 pour tous, sauf l'administrateur et son auteur
    if r.hidden and not (user and (user.is_admin or user.id == r.author_id)):
        raise HTTPException(404, "not_found")
    liked = False
    if user:
        liked = (await db.execute(select(Like).where(Like.user_id == user.id, Like.resource_id == rid))).first() is not None
    return to_doc(r, name or "", liked)


@router.get("/sitemap")
async def sitemap(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Resource.id, Resource.updated_at, Resource.kind, Resource.clang).where(Resource.hidden.is_(False)).order_by(Resource.updated_at.desc()).limit(45000))).all()
    labs = set((await db.execute(select(User.username).where(User.is_lab.is_(True), User.hidden.is_(False)))).scalars().all())
    # Pages de tag (au moins 2 ressources, pour éviter les pages trop maigres)
    tag = func.unnest(Resource.tags).label("tag")
    tsub = select(Resource.kind, tag).where(Resource.hidden.is_(False)).subquery()
    tags = (await db.execute(select(tsub.c.kind, tsub.c.tag).group_by(tsub.c.kind, tsub.c.tag).having(func.count() >= 2))).all()
    # Auteurs ayant publié : leurs profils publics sont indexables
    authors = (await db.execute(
        select(Resource.author_handle, func.max(Resource.updated_at))
        .where(Resource.author_handle != "", Resource.hidden.is_(False),
               ~Resource.author_handle.in_(select(User.username).where(User.hidden.is_(True))))
        .group_by(Resource.author_handle)
    )).all()
    return {"items": [{"id": i, "updatedAt": _ms(u), "kind": k, "clang": c or ""} for i, u, k, c in rows],
            "authors": [{"name": a, "updatedAt": _ms(u), "lab": a in labs} for a, u in authors],
            "tags": [{"kind": k, "tag": t} for k, t in tags]}


@router.get("/tags")
async def known_tags(kind: str = Query("", max_length=20), db: AsyncSession = Depends(get_db)):
    """Tags existants, les plus utilisés d'abord : suggestions du formulaire de publication."""
    tag = func.unnest(Resource.tags).label("tag")
    stmt = select(tag).where(Resource.hidden.is_(False))
    if kind in KINDS:
        stmt = stmt.where(Resource.kind == kind)
    sub = stmt.subquery()
    rows = (await db.execute(select(sub.c.tag, func.count()).group_by(sub.c.tag).order_by(func.count().desc()).limit(200))).all()
    return {"items": [[t, n] for t, n in rows]}


# ---------- Écriture ----------

class ResourceIn(BaseModel):
    kind: str
    name: str
    authorHandle: str = ""
    description: str = Field("", max_length=240)
    tags: list[str] = []
    clang: str = ""
    license: str = ""
    sourceUrl: str = Field("", max_length=500)
    sub: str = ""
    data: dict = {}


def _validate(body: ResourceIn, max_bytes: int) -> tuple[dict, int]:
    if body.kind not in KINDS:
        raise HTTPException(400, "invalid_kind")
    if not NAME_RE.match(body.name):
        raise HTTPException(400, "invalid_name")
    if body.clang not in CLANGS or body.license not in LICENSES:
        raise HTTPException(400, "invalid_meta")
    # Lien vers l'origine (dépôt, article, page Hugging Face…) : http(s) uniquement
    if body.sourceUrl and not re.match(r"^https?://[^\s<>\"]+$", body.sourceUrl):
        raise HTTPException(400, "invalid_source_url")
    if body.sub not in SUBS[body.kind]:
        raise HTTPException(400, "invalid_sub")
    if any(not TAG_RE.match(t) for t in body.tags) or len(body.tags) > 10:
        raise HTTPException(400, "invalid_tags")
    if len(json.dumps(body.data)) > max_bytes:
        raise HTTPException(413, "too_large")
    d, rows = dict(body.data), 0
    if body.kind == "context":
        d = {"system": str(d.get("system", "")), "knowledge": str(d.get("knowledge", "")),
             "examples": [{"input": str(e.get("input", "")), "output": str(e.get("output", ""))}
                          for e in (d.get("examples") or []) if isinstance(e, dict)][:200]}
        if not (d["system"] or d["knowledge"] or d["examples"]):
            raise HTTPException(400, "empty_context")
    elif body.kind == "prompt":
        d = {"template": str(d.get("template", ""))}
        if not d["template"].strip():
            raise HTTPException(400, "empty_template")
    elif body.kind == "dataset":
        jsonl = str(d.get("jsonl", ""))
        if jsonl.strip():
            try:
                rows, fmt, preview = scan_jsonl(jsonl.splitlines())
            except DatasetError as e:
                raise HTTPException(400, str(e)) from e
            d = {"jsonl": jsonl, "preview": preview}
        else:
            d = {"jsonl": "", "preview": []}
    elif body.kind == "agent":
        # Agent : rôle, étapes, serveurs MCP et contextes branchés, garde-fous
        ids = lambda k: [str(x) for x in (d.get(k) or []) if ID_RE.match(str(x))][:10]
        steps = [str(x).strip()[:500] for x in (d.get("steps") or []) if str(x).strip()][:30]
        d = {"instructions": str(d.get("instructions", "")).strip()[:8000], "steps": steps,
             "framework": d.get("framework") if d.get("framework") in AGENT_FRAMEWORKS else "other",
             "mcpIds": ids("mcpIds"), "contextIds": ids("contextIds"), "guardrails": str(d.get("guardrails", "")).strip()[:4000]}
        if not d["instructions"]:
            raise HTTPException(400, "empty_instructions")
    elif body.kind == "skill":
        # Skill : un paquet d'instructions chargé à la demande (format SKILL.md)
        name = str(d.get("skillName", "")).strip()
        if not re.match(r"^[a-z0-9-]{1,64}$", name):
            raise HTTPException(400, "invalid_skill_name")
        d = {"skillName": name, "whenToUse": str(d.get("whenToUse", "")).strip()[:1024],
             "instructions": str(d.get("instructions", "")).strip()[:20000], "resources": str(d.get("resources", "")).strip()[:4000]}
        if not d["instructions"]:
            raise HTTPException(400, "empty_instructions")
    elif body.kind == "eval":
        # Évaluation : cas de test (entrée, attendu) + méthode de notation
        cases = [{"input": str(c.get("input", ""))[:4000], "expected": str(c.get("expected", ""))[:4000]}
                 for c in (d.get("cases") or []) if isinstance(c, dict) and str(c.get("input", "")).strip()][:500]
        if not cases:
            raise HTTPException(400, "empty_cases")
        try:
            thr = max(0, min(100, int(d.get("threshold") or 80)))
        except (TypeError, ValueError):
            thr = 80
        d = {"cases": cases, "metric": d.get("metric") if d.get("metric") in EVAL_METRICS else "contains",
             "criteria": str(d.get("criteria", "")).strip()[:4000], "threshold": thr,
             "evaluatesId": str(d.get("evaluatesId") or "") if ID_RE.match(str(d.get("evaluatesId") or "-")) and d.get("evaluatesId") else ""}
    elif body.kind == "rag":
        # Pipeline RAG : sources, découpage, embeddings, base vectorielle, recherche, prompt
        def n(k, lo, hi, dflt):
            try:
                return max(lo, min(hi, int(d.get(k))))
            except (TypeError, ValueError):
                return dflt
        d = {"sources": str(d.get("sources", "")).strip()[:2000], "chunkSize": n("chunkSize", 50, 20000, 800),
             "chunkOverlap": n("chunkOverlap", 0, 5000, 100), "embedding": str(d.get("embedding", "")).strip()[:120],
             "vectorStore": d.get("vectorStore") if d.get("vectorStore") in VECTOR_STORES else "other",
             "topK": n("topK", 1, 100, 5), "reranker": str(d.get("reranker", "")).strip()[:120],
             "promptTemplate": str(d.get("promptTemplate", "")).strip()[:8000]}
        if not d["embedding"] or not d["promptTemplate"]:
            raise HTTPException(400, "empty_rag")
    elif body.kind == "harness":
        # Harness : environnement d'exécution d'un agent (instructions, outils, permissions, hooks, MCP)
        lines = lambda k: [str(x).strip()[:200] for x in (d.get(k) or []) if str(x).strip()][:50]
        d = {"harness": d.get("harness") if d.get("harness") in HARNESSES else "other",
             "instructions": str(d.get("instructions", "")).strip()[:20000], "allow": lines("allow"), "deny": lines("deny"),
             "hooks": str(d.get("hooks", "")).strip()[:8000],
             "mcpIds": [str(x) for x in (d.get("mcpIds") or []) if ID_RE.match(str(x))][:10]}
        if not d["instructions"]:
            raise HTTPException(400, "empty_instructions")
    elif body.kind == "tool":
        # Serveur MCP : lancé par une commande (stdio) ou joint par une URL (HTTP)
        tool_name = str(d.get("toolName", "")).strip()
        if not TOOL_NAME_RE.match(tool_name):
            raise HTTPException(400, "invalid_tool_name")
        transport = d.get("transport") if d.get("transport") in ("stdio", "http") else "stdio"
        command = str(d.get("command", "")).strip()[:500]
        url = str(d.get("url", "")).strip()[:500]
        if transport == "stdio" and not command:
            raise HTTPException(400, "missing_command")
        if transport == "http" and not re.match(r"^https?://[^\s<>\"]+$", url):
            raise HTTPException(400, "invalid_mcp_url")
        env = [str(k).strip()[:80] for k in (d.get("env") or []) if str(k).strip()][:20]
        d = {"toolName": tool_name, "transport": transport, "command": command if transport == "stdio" else "",
             "url": url if transport == "http" else "", "env": env, "notes": str(d.get("notes", ""))[:4000]}
    elif body.kind == "model":
        # Modèle publié par un Lab : fiche descriptive + lien vers les poids (hébergés ailleurs)
        weights = str(d.get("weightsUrl", "")).strip()[:500]
        if not re.match(r"^https?://[^\s<>\"]+$", weights):
            raise HTTPException(400, "invalid_weights_url")
        fmt = d.get("format") if d.get("format") in MODEL_FORMATS else "safetensors"
        fam = d.get("family") if d.get("family") in MODEL_FAMILIES else "other"
        try:
            ctx = max(0, min(10_000_000, int(d.get("contextLength") or 0)))
        except (TypeError, ValueError):
            ctx = 0
        def txt(k, n):
            return str(d.get(k) or "").strip()[:n]

        def num(k, lo, hi, cast=float):
            try:
                v = cast(d.get(k))
                return v if lo <= v <= hi else None
            except (TypeError, ValueError):
                return None

        def day(k):
            v = txt(k, 10)
            return v if re.match(r"^\d{4}-\d{2}-\d{2}$", v) else ""

        ids = [str(x) for x in (d.get("datasetIds") or []) if ID_RE.match(str(x))][:5]
        bench = [{"name": str(b.get("name", "")).strip()[:60], "score": str(b.get("score", "")).strip()[:20]}
                 for b in (d.get("benchmarks") or []) if isinstance(b, dict) and str(b.get("name", "")).strip()][:20]
        d = {"baseModel": txt("baseModel", 200), "family": fam, "params": txt("params", 20), "format": fmt,
             "quant": txt("quant", 40), "contextLength": ctx, "weightsUrl": weights, "notes": str(d.get("notes", ""))[:8000],
             # Entraînement
             "datasetIds": ids, "loraId": txt("loraId", 120) if ID_RE.match(txt("loraId", 120) or "-") else "",
             "epochs": num("epochs", 0, 1000, int), "trainedAt": day("trainedAt"),
             # Matériel requis
             "vramGb": num("vramGb", 0, 2000), "cpuOk": bool(d.get("cpuOk")), "speed": txt("speed", 80),
             # Usage et langues
             "languages": [c for c in (d.get("languages") or []) if isinstance(c, str) and re.match(r"^[a-z]{2,5}$", c)][:12],
             "chatTemplate": d.get("chatTemplate") if d.get("chatTemplate") in CHAT_TEMPLATES else "",
             "useCases": txt("useCases", 2000), "limits": txt("limits", 2000),
             # Évaluations et version
             "benchmarks": bench, "version": txt("version", 30), "releasedAt": day("releasedAt"), "changelog": txt("changelog", 4000)}
    elif body.kind == "lora":
        def num(k, default, cast=float):
            try:
                return cast(d.get(k, default))
            except (TypeError, ValueError):
                return default
        d = {"baseModel": str(d.get("baseModel", "")).strip()[:200],
             "r": num("r", 16, int), "alpha": num("alpha", 32, int), "dropout": num("dropout", 0.05),
             "lr": num("lr", 0.0002), "epochs": num("epochs", 3, int), "batch": num("batch", 4, int),
             "gradAcc": num("gradAcc", 4, int), "seqLen": num("seqLen", 2048, int),
             "targets": [str(t)[:40] for t in (d.get("targets") or [])][:20],
             "datasetId": d.get("datasetId") or None, "notes": str(d.get("notes", ""))[:4000]}
        if not d["baseModel"]:
            raise HTTPException(400, "missing_base_model")
    # Pour tous les types (sauf Modèles, qui ont leurs propres champs) : version, historique, « Testé sur »
    if body.kind != "model":
        d = {**d, "version": str(body.data.get("version") or "").strip()[:30],
             "changelog": str(body.data.get("changelog") or "").strip()[:4000], "tests": _tests(body.data)}
    # Serveurs MCP et harness : ce que la ressource peut faire (niveau de risque)
    if body.kind in ("tool", "harness"):
        acc = body.data.get("access") if isinstance(body.data.get("access"), dict) else {}
        d["access"] = {k: bool(acc.get(k)) for k in ACCESS}
    if body.kind in TARGET_KINDS:
        raw = body.data
        fam = raw.get("targetFamily") if raw.get("targetFamily") in TARGET_FAMILIES else ""
        mid = str(raw.get("targetModelId") or "")
        d = {**d, "targetFamily": fam, "targetModel": str(raw.get("targetModel") or "").strip()[:80] if fam else "",
             "targetModelId": mid if fam and ID_RE.match(mid or "-") and mid else ""}
    return d, rows


ACCESS = ("read", "write", "network", "exec")
TEST_RESULTS = ("pass", "partial", "fail")


def _tests(raw: dict) -> list[dict]:
    """« Testé sur » : modèle, date, résultat (réussi / partiel / échec), score optionnel, remarque."""
    out = []
    for x in (raw.get("tests") or [])[:20]:
        if not isinstance(x, dict) or not str(x.get("model", "")).strip():
            continue
        day = str(x.get("date") or "")[:10]
        try:
            score = None if x.get("score") in (None, "") else round(max(0.0, min(100.0, float(x.get("score")))), 1)
        except (TypeError, ValueError):
            score = None
        out.append({"model": str(x["model"]).strip()[:80], "date": day if re.match(r"^\d{4}-\d{2}-\d{2}$", day) else "",
                    "result": x.get("result") if x.get("result") in TEST_RESULTS else "pass", "score": score,
                    "note": str(x.get("note") or "").strip()[:300]})
    return out


@router.put("/resources/{rid}", include_in_schema=False)
async def put_resource(rid: str, body: ResourceIn, background: BackgroundTasks, create: bool = Query(False), db: AsyncSession = Depends(get_db),
                       user: User = Depends(require_user)):
    if not ID_RE.match(rid):
        raise HTTPException(400, "invalid_id")
    if body.kind == "tool":
        body.sub = "mcp"                                  # la catégorie ne contient plus que des serveurs MCP
    # Les modèles sont réservés aux Labs (et à l'administrateur)
    if body.kind == "model" and not (user.is_admin or user.is_lab):
        raise HTTPException(403, "lab_only")
    data, rows = _validate(body, get_settings().max_resource_kb * 1024)
    r = await db.get(Resource, rid)
    created = False
    if r is not None and create:
        # Nouvelle ressource : l'identifiant est déjà pris
        raise HTTPException(409, "exists")
    if r is not None:
        if r.author_id != user.id and not user.is_admin:
            raise HTTPException(403, "forbidden")
        if r.kind != body.kind:
            raise HTTPException(400, "kind_immutable")
    else:
        if not user.is_admin:
            # Un membre publie sous son propre nom : /<type>/<son-nom>/<ressource>
            if not rid.startswith(f"{user.username}--"):
                raise HTTPException(403, "forbidden")
            key = f"rate:publish:{user.id}:{int(time.time() // 86400)}"
            n = await redis.incr(key)
            if n == 1:
                await redis.expire(key, 90000)
            if n > PUBLISH_PER_DAY:
                raise HTTPException(429, "rate_limited")
        r = Resource(id=rid, kind=body.kind, author_id=user.id, uses=0, likes_count=0, row_count=0)
        db.add(r)
        created = True
    # Seul l'administrateur choisit librement le nom d'auteur affiché
    handle = body.authorHandle[:30] if user.is_admin else (r.author_handle or user.username)
    r.name, r.author_handle, r.description = body.name, handle, body.description
    r.tags, r.clang, r.license, r.sub = body.tags, body.clang, body.license, body.sub
    r.source_url = body.sourceUrl.strip()
    if body.kind == "dataset" and not data["jsonl"] and r.blob_key:
        # conserve l'aperçu du fichier stocké, garde les autres champs modifiés
        data = {**(r.data or {}), **{k: v for k, v in data.items() if k != "jsonl"}}
    else:
        if body.kind == "dataset" and data["jsonl"]:
            r.blob_key = None
        r.row_count = rows if body.kind == "dataset" and data.get("jsonl") else r.row_count
    r.data = data
    await db.commit()
    await bump_cache()
    # Nouvelle fiche : e-mail « votre fiche est en ligne » à l'auteur, copie cachée à l'éditeur
    if created and user.email:
        s = get_settings()
        url = f"{s.public_origin}/{DETAIL_SLUGS_FR[r.kind]}/{r.name}-{short_id(r.id)}"
        subject, text, html = mail("published", "fr", site=s.site_name, origin=s.public_origin, user=user.username,
                                   name=r.name, kind=KIND_LABELS_FR[r.kind], url=url)
        background.add_task(send_mail, user.email, subject, text, True, html)
    return await get_resource(rid, db, user)


@router.delete("/resources/{rid}", include_in_schema=False)
async def delete_resource(rid: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_user)):
    r = await db.get(Resource, rid)
    if r is None:
        raise HTTPException(404, "not_found")
    if r.author_id != user.id and not user.is_admin:
        raise HTTPException(403, "forbidden")
    if r.blob_key and get_settings().s3_enabled:
        await storage.delete(r.blob_key)
    await db.delete(r)
    await db.commit()
    await bump_cache()
    return {"ok": True}


@router.post("/resources/{rid}/dataset", include_in_schema=False)
async def upload_dataset(rid: str, file: UploadFile = File(...), db: AsyncSession = Depends(get_db),
                         user: User = Depends(require_user)):
    s = get_settings()
    if not s.s3_enabled:
        raise HTTPException(503, "object_storage_disabled")
    r = await db.get(Resource, rid)
    if r is None or r.kind != "dataset":
        raise HTTPException(404, "not_found")
    if r.author_id != user.id and not user.is_admin:
        raise HTTPException(403, "forbidden")
    limit = s.max_dataset_mb * 1024 * 1024
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    try:
        size = 0
        with os.fdopen(fd, "wb") as out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > limit:
                    raise HTTPException(413, "too_large")
                out.write(chunk)
        try:
            with open(path, "rb") as fh:
                rows, fmt, preview = scan_jsonl(fh)
        except (DatasetError, UnicodeDecodeError) as e:
            raise HTTPException(400, str(e) if isinstance(e, DatasetError) else "invalid_encoding") from e
        key = f"datasets/{rid}.jsonl"
        await storage.put_file(key, path)
    finally:
        if os.path.exists(path):
            os.remove(path)
    r.blob_key, r.row_count, r.sub = key, rows, fmt or r.sub
    r.data = {"jsonl": "", "preview": preview}
    await db.commit()
    await bump_cache()
    return await get_resource(rid, db, user)


@router.get("/resources/{rid}/download")
async def download(rid: str, db: AsyncSession = Depends(get_db)):
    r = await db.get(Resource, rid)
    if r is None:
        raise HTTPException(404, "not_found")
    await db.execute(update(Resource).where(Resource.id == rid).values(uses=Resource.uses + 1))
    await db.commit()
    if r.kind == "dataset" and r.blob_key:
        return RedirectResponse(await storage.presigned_url(r.blob_key, f"{r.name}.jsonl"), status_code=302)
    if r.kind == "dataset":
        return PlainTextResponse((r.data or {}).get("jsonl", "").strip() + "\n", media_type="application/x-ndjson",
                                 headers={"Content-Disposition": f'attachment; filename="{r.name}.jsonl"'})
    raise HTTPException(400, "use_client_export")


@router.post("/resources/{rid}/like", include_in_schema=False)
async def toggle_like(rid: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_user)):
    if await db.get(Resource, rid) is None:
        raise HTTPException(404, "not_found")
    existing = (await db.execute(select(Like).where(Like.user_id == user.id, Like.resource_id == rid))).first()
    if existing:
        await db.execute(delete(Like).where(Like.user_id == user.id, Like.resource_id == rid))
        await db.execute(update(Resource).where(Resource.id == rid).values(likes_count=Resource.likes_count - 1))
    else:
        db.add(Like(user_id=user.id, resource_id=rid))
        await db.execute(update(Resource).where(Resource.id == rid).values(likes_count=Resource.likes_count + 1))
    await db.commit()
    await bump_cache()
    likes = (await db.execute(select(Resource.likes_count).where(Resource.id == rid))).scalar_one()
    return {"liked": not existing, "likes": likes}


@router.post("/resources/{rid}/use", include_in_schema=False)
async def mark_use(rid: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(update(Resource).where(Resource.id == rid).values(uses=Resource.uses + 1))
    await db.commit()
    if res.rowcount == 0:
        raise HTTPException(404, "not_found")
    return {"ok": True}
