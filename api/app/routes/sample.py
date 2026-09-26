import json
import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .. import llm
from ..config import get_settings
from ..models import User
from ..redis import redis
from ..security import require_admin

router = APIRouter(prefix="/api", tags=["sandbox"])


class SampleIn(BaseModel):
    input: str | list[dict]
    tier: str = "default"


@router.post("/sample")
async def sample(body: SampleIn, user: User = Depends(require_admin)):
    s = get_settings()
    if not s.llm_enabled:
        raise HTTPException(503, "disabled")
    key = f"rate:sample:{user.id}:{int(time.time() // 60)}"
    n = await redis.incr(key)
    if n == 1:
        await redis.expire(key, 70)
    if n > s.sample_rate_per_min:
        raise HTTPException(429, "rate_limited")
    try:
        llm.to_turns(body.input)
    except llm.LLMError as e:
        raise HTTPException(400, str(e)) from e
    tier = body.tier if body.tier in ("quick", "default", "complex") else "default"

    async def events():
        try:
            async for ev in llm.stream(body.input, tier):
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        except llm.LLMError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
