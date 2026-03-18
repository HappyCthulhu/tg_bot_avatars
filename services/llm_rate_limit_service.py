from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from providers import RedisProvider


class LLMRateLimitService:
    def __init__(self, redis_provider: RedisProvider, limit_seconds: int = 2) -> None:
        self._redis_provider = redis_provider
        self._limit_seconds = limit_seconds

    async def allow_request(self, user_id: int) -> bool:
        """Check if request is allowed."""
        key = f"llm_rate:{user_id}"
        counter = await self._redis_provider.incr(key)
        if counter == 1:
            await self._redis_provider.expire(key, self._limit_seconds)
        return counter == 1
