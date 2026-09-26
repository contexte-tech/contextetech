"""Bac à sable : streaming depuis Anthropic ou une API compatible OpenAI (Ollama, vLLM…)."""
import json
from collections.abc import AsyncIterator

import httpx

from .config import get_settings


class LLMError(Exception):
    pass


def to_turns(inp) -> list[dict]:
    if isinstance(inp, str):
        return [{"role": "user", "content": inp}]
    if not isinstance(inp, list):
        raise LLMError("invalid_input")
    turns = [
        {"role": t["role"], "content": str(t.get("content", ""))}
        for t in inp
        if isinstance(t, dict) and t.get("role") in ("user", "assistant")
    ]
    if not turns or turns[-1]["role"] != "user":
        raise LLMError("invalid_input")
    return turns


async def stream(inp, tier: str) -> AsyncIterator[dict]:
    """Produit {"delta": str} puis {"done": True, "truncated": bool}."""
    s = get_settings()
    turns = to_turns(inp)
    model = s.llm_models.get(tier) or s.llm_models["default"]
    if not model:
        raise LLMError("no_model")

    if s.llm_provider == "anthropic":
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=s.anthropic_api_key, timeout=180)
        try:
            async with client.messages.stream(model=model, max_tokens=s.llm_max_tokens, messages=turns) as st:
                async for text in st.text_stream:
                    yield {"delta": text}
                final = await st.get_final_message()
            yield {"done": True, "truncated": final.stop_reason == "max_tokens"}
        except anthropic.APIError as e:
            raise LLMError(getattr(e, "message", str(e))[:200]) from e
        return

    if s.llm_provider == "openai":
        headers = {"Content-Type": "application/json"}
        if s.llm_api_key:
            headers["Authorization"] = f"Bearer {s.llm_api_key}"
        body = {"model": model, "messages": turns, "max_tokens": s.llm_max_tokens, "stream": True}
        finish = None
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(180, connect=10)) as client:
                async with client.stream("POST", s.llm_base_url.rstrip("/") + "/chat/completions",
                                         json=body, headers=headers) as r:
                    if r.status_code >= 400:
                        raise LLMError(f"upstream_{r.status_code}")
                    async for line in r.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        payload = line[5:].strip()
                        if payload == "[DONE]":
                            break
                        try:
                            choice = json.loads(payload)["choices"][0]
                        except (ValueError, KeyError, IndexError):
                            continue
                        delta = (choice.get("delta") or {}).get("content")
                        if delta:
                            yield {"delta": delta}
                        finish = choice.get("finish_reason") or finish
        except httpx.HTTPError as e:
            raise LLMError("upstream_unreachable") from e
        yield {"done": True, "truncated": finish == "length"}
        return

    raise LLMError("disabled")
