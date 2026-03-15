from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib import error, request

from django.conf import settings


async def generate_reply(messages: list[dict[str, str]]) -> str:
    api_key: str = settings.OPENAI_API_KEY
    model: str = settings.OPENAI_MODEL

    payload = {
        "model": model,
        "messages": messages,
    }

    def _call_openai() -> str:
        req = request.Request(
            url="https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=40) as response:  # noqa: S310
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            return f"LLM HTTP error: {exc.code}"
        except error.URLError:
            return "LLM недоступна. Попробуй позже."

        try:
            parsed: dict[str, Any] = json.loads(raw)
            content = parsed["choices"][0]["message"]["content"]
            return str(content).strip() or "Пустой ответ от LLM."
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            return "Не удалось распарсить ответ LLM."

    return await asyncio.to_thread(_call_openai)
