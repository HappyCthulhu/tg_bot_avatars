from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.conf import settings

from domain import Message

if TYPE_CHECKING:
    from providers import RedisProvider


class ShortMemoryService:
    SHORT_MEMORY_SIZE = settings.SHORT_MEMORY_SIZE
    SHORT_MEMORY_TTL = settings.SHORT_MEMORY_TTL

    def __init__(self, redis_provider: RedisProvider) -> None:
        self._redis = redis_provider

    def _dialog_key(self, user_id: int, avatar_id: int) -> str:
        return f"dialog:{user_id}:{avatar_id}"

    async def add_message(self, user_id: int, avatar_id: int, message: Message) -> None:
        key = self._dialog_key(user_id, avatar_id)
        # TODO: стоит ли json.dumps вынести в to_redis_dict?
        await self._redis.lpush(key, json.dumps(message.to_redis_dict(), ensure_ascii=False))
        await self._redis.ltrim(key, 0, self.SHORT_MEMORY_SIZE - 1)
        await self._redis.expire(key, self.SHORT_MEMORY_TTL)

    async def get_messages(self, user_id: int, avatar_id: int) -> list[Message]:
        key = self._dialog_key(user_id, avatar_id)
        raw_values = await self._redis.lrange(key, 0, self.SHORT_MEMORY_SIZE - 1)
        messages = [Message.from_redis_dict(json.loads(raw)) for raw in raw_values]
        messages.reverse()
        return messages

    async def clear_dialog(self, user_id: int, avatar_id: int) -> None:
        key = self._dialog_key(user_id, avatar_id)
        await self._redis.ltrim(key, 1, 0)
