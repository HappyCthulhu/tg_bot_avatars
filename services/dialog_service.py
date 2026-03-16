from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils import timezone

from domain import Message

if TYPE_CHECKING:
    from llm import LLMService, PromptBuilder
    from server.apps.avatars.models import Avatar
    from server.apps.users.models import User
    from services.short_memory_service import ShortMemoryService


class DialogService:
    def __init__(
        self,
        short_memory_service: ShortMemoryService,
        prompt_builder: PromptBuilder,
        llm_service: LLMService,
    ) -> None:
        self._short_memory_service = short_memory_service
        self._prompt_builder = prompt_builder
        self._llm_service = llm_service

    async def handle_user_message(
        self,
        user: User,
        avatar: Avatar,
        text: str,
    ) -> str:
        short_memory = await self._short_memory_service.get_messages(user.id, avatar.id)
        prompt = self._prompt_builder.build_dialog_prompt(
            system_prompt=avatar.system_prompt,
            short_memory=short_memory,
            user_message=text,
        )
        reply = await self._llm_service.generate(prompt)

        now = timezone.now()
        await self._short_memory_service.add_message(
            user.id,
            avatar.id,
            Message(sender="user", text=text, timestamp=now),
        )
        await self._short_memory_service.add_message(
            user.id,
            avatar.id,
            Message(sender="assistant", text=reply, timestamp=timezone.now()),
        )
        return reply
