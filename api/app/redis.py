from redis.asyncio import Redis

from .config import get_settings

redis: Redis = Redis.from_url(get_settings().redis_url, decode_responses=True)


async def cache_version() -> str:
    return await redis.get("cache:ver") or "0"


async def bump_cache() -> None:
    await redis.incr("cache:ver")
