from __future__ import annotations

from typing import TYPE_CHECKING

from django.utils import timezone

from domain import Message

if TYPE_CHECKING:
    from llm import LLMService, PromptBuilder
    from server.apps.avatars.models import Avatar
    from server.apps.users.models import User
    from services.short_memory_service import ShortMemoryService
    from services.streaming_service import StreamingService


class DialogService:
    def __init__(
        self,
        short_memory_service: ShortMemoryService,
        prompt_builder: PromptBuilder,
        llm_service: LLMService,
        streaming_service: StreamingService | None = None,
    ) -> None:
        self._short_memory_service = short_memory_service
        self._prompt_builder = prompt_builder
        self._llm_service = llm_service
        self._streaming_service = streaming_service

    async def handle_user_message(
        self,
        user: User,
        avatar: Avatar,
        text: str,
    ) -> str:
        prompt = await self._build_dialog_prompt(user=user, avatar=avatar, user_text=text)
        reply = await self._llm_service.generate(prompt)
        await self._save_dialog_messages(user=user, avatar=avatar, user_text=text, assistant_text=reply)
        return reply

    async def handle_user_message_stream(
        self,
        user: User,
        avatar: Avatar,
        text: str,
        chat_id: int,
    ) -> str:
        if self._streaming_service is None:
            msg = "StreamingService is required for handle_user_message_stream."
            raise RuntimeError(msg)

        prompt = await self._build_dialog_prompt(user=user, avatar=avatar, user_text=text)
        reply = await self._streaming_service.stream_reply(
            chat_id=chat_id,
            messages=prompt,
            llm_service=self._llm_service,
        )
        await self._save_dialog_messages(user=user, avatar=avatar, user_text=text, assistant_text=reply)
        return reply

    async def _build_dialog_prompt(self, user: User, avatar: Avatar, user_text: str) -> list[dict[str, str]]:
        """Get messages from short memory and build dialog prompt."""
        short_memory = await self._short_memory_service.get_messages(user.id, avatar.id)
        return self._prompt_builder.build_dialog_prompt(
            system_prompt=avatar.system_prompt,
            short_memory=short_memory,
            user_message=user_text,
        )

    async def _save_dialog_messages(self, user: User, avatar: Avatar, user_text: str, assistant_text: str) -> None:
        """Save user and assistant messages to short memory."""
        now = timezone.now()
        await self._short_memory_service.add_message(
            user.id,
            avatar.id,
            Message(sender="user", text=user_text, timestamp=now),
        )
        await self._short_memory_service.add_message(
            user.id,
            avatar.id,
            Message(sender="assistant", text=assistant_text, timestamp=timezone.now()),
        )
