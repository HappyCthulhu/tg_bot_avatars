from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from providers import RedisProvider


class FactTriggerService:
    def __init__(self, redis_provider: RedisProvider, interval: int = 5) -> None:
        self._redis_provider = redis_provider
        self._interval = interval

    async def bump_and_should_trigger(self, user_id: int, avatar_id: int) -> bool:
        """Update counter and check if should trigger."""
        counter_key = f"dialog_counter:{user_id}:{avatar_id}"
        counter = await self._redis_provider.incr(counter_key)
        return counter % self._interval == 0
