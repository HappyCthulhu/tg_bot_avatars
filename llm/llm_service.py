from __future__ import annotations

import os
from typing import Any

from openai import AsyncOpenAI


class LLMService:
    def __init__(self) -> None:
        self._api_key = os.environ["OPENAI_API_KEY"]
        self._model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self._client = AsyncOpenAI(api_key=self._api_key)

    async def generate(self, messages: list[dict[str, Any]]) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )
        content = response.choices[0].message.content
        return content.strip() if content else "Пустой ответ от LLM."
