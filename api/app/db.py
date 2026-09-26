import ssl
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import get_settings


def _ssl_arg(s):
    mode = (s.postgres_sslmode or "disable").lower()
    if mode == "disable":
        return False
    if mode == "verify-full":
        ctx = ssl.create_default_context(cafile=s.postgres_sslrootcert or None)
        ctx.check_hostname = True
        return ctx
    if mode in ("verify-ca",):
        ctx = ssl.create_default_context(cafile=s.postgres_sslrootcert or None)
        ctx.check_hostname = False
        return ctx
    return "require"


def make_engine():
    s = get_settings()
    return create_async_engine(
        s.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=10,
        connect_args={"ssl": _ssl_arg(s), "timeout": 10},
    )


engine = make_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
