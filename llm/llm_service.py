from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from openai import AsyncOpenAI

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


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

    async def stream_generate(self, messages: list[dict[str, Any]]) -> AsyncIterator[str]:
        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield delta
