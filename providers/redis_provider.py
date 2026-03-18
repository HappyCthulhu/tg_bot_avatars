from __future__ import annotations

from django.conf import settings
from redis import asyncio as aioredis


class RedisProvider:
    def __init__(self) -> None:
        self._client = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    async def lpush(self, key: str, value: str) -> None:
        await self._client.lpush(key, value)

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        values = await self._client.lrange(key, start, end)
        return list(values)

    async def ltrim(self, key: str, start: int, end: int) -> None:
        await self._client.ltrim(key, start, end)

    async def expire(self, key: str, seconds: int) -> None:
        await self._client.expire(key, seconds)

    async def incr(self, key: str) -> int:
        return int(await self._client.incr(key))
