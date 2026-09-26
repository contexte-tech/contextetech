"""python -m app.cli bootstrap | seed"""
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import select

from .config import get_settings
from .db import SessionLocal
from .formats import scan_jsonl
from .models import Resource, User
from .security import hash_password


async def bootstrap():
    s = get_settings()
    if not (s.admin_username and s.admin_password):
        return
    async with SessionLocal() as db:
        name = s.admin_username.strip().lower()
        if (await db.execute(select(User).where(User.username == name))).scalar_one_or_none():
            return
        db.add(User(username=name, password_hash=hash_password(s.admin_password), is_admin=True))
        await db.commit()
        print(f"Administrateur {name} créé.")


async def seed():
    items = json.loads((Path(__file__).parent / "seed.json").read_text(encoding="utf-8"))
    async with SessionLocal() as db:
        admin = (await db.execute(select(User).where(User.is_admin.is_(True)).limit(1))).scalar_one_or_none()
        n = 0
        for it in items:
            if await db.get(Resource, it["id"]):
                continue
            data, rows = it["data"], 0
            if it["kind"] == "dataset":
                rows, _, preview = scan_jsonl(data["jsonl"].splitlines())
                data = {**data, "preview": preview}
            db.add(Resource(id=it["id"], kind=it["kind"], name=it["name"], author_id=admin.id if admin else None,
                            author_handle=it.get("authorHandle", ""), description=it.get("description", ""),
                            tags=it.get("tags", []), clang=it.get("clang", ""), license=it.get("license", ""),
                            sub=it.get("sub", ""), data=data, row_count=rows))
            n += 1
        await db.commit()
        print(f"{n} ressource(s) d'exemple ajoutée(s).")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    asyncio.run({"bootstrap": bootstrap, "seed": seed}[cmd]())
