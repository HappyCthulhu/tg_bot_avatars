from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from django.conf import settings
from django.utils import timezone
from loguru import logger

from domain import Message
from services.exceptions import LLMRateLimitExceededError
from utils import count_prompt_tokens

if TYPE_CHECKING:
    from llm import LLMService, PromptBuilder
    from server.apps.avatars.models import Avatar
    from server.apps.users.models import User
    from services.fact_trigger_service import FactTriggerService
    from services.llm_rate_limit_service import LLMRateLimitService
    from services.memory_service import MemoryService
    from services.short_memory_service import ShortMemoryService
    from services.streaming_service import StreamingService


class DialogService:
    def __init__(  # noqa: PLR0913
        self,
        short_memory_service: ShortMemoryService,
        prompt_builder: PromptBuilder,
        llm_service: LLMService,
        memory_service: MemoryService | None = None,
        fact_trigger_service: FactTriggerService | None = None,
        llm_rate_limit_service: LLMRateLimitService | None = None,
        streaming_service: StreamingService | None = None,
    ) -> None:
        self._short_memory_service = short_memory_service
        self._prompt_builder = prompt_builder
        self._llm_service = llm_service
        self._memory_service = memory_service
        self._fact_trigger_service = fact_trigger_service
        self._llm_rate_limit_service = llm_rate_limit_service
        self._streaming_service = streaming_service
        self._background_tasks: set[asyncio.Task[None]] = set()

    async def handle_user_message(
        self,
        user: User,
        avatar: Avatar,
        text: str,
    ) -> str:
        await self._ensure_rate_limit(user.id)
        prompt = await self._build_dialog_prompt(user=user, avatar=avatar, user_text=text)
        reply = await self._llm_service.generate(prompt)
        await self._save_dialog_messages(user=user, avatar=avatar, user_text=text, assistant_text=reply)
        await self._maybe_trigger_fact_extraction(user_id=user.id, avatar_id=avatar.id)
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

        await self._ensure_rate_limit(user.id)
        prompt = await self._build_dialog_prompt(user=user, avatar=avatar, user_text=text)
        reply = await self._streaming_service.stream_reply(
            chat_id=chat_id,
            messages=prompt,
            llm_service=self._llm_service,
        )
        await self._save_dialog_messages(user=user, avatar=avatar, user_text=text, assistant_text=reply)
        await self._maybe_trigger_fact_extraction(user_id=user.id, avatar_id=avatar.id)
        return reply

    async def _build_dialog_prompt(self, user: User, avatar: Avatar, user_text: str) -> list[dict[str, str]]:
        """Get messages from short memory and build dialog prompt."""
        short_memory = await self._short_memory_service.get_messages(user.id, avatar.id)
        long_term_facts = []
        if self._memory_service is not None:
            long_term_facts = await self._memory_service.get_facts_for_prompt(user.id, avatar.id)

        while True:
            prompt = self._prompt_builder.build_dialog_prompt(
                system_prompt=avatar.system_prompt,
                short_memory=short_memory,
                user_message=user_text,
                long_term_facts=long_term_facts,
            )
            if count_prompt_tokens(prompt) <= settings.MAX_PROMPT_TOKENS or not short_memory:
                return prompt
            short_memory = short_memory[1:]

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

    async def _maybe_trigger_fact_extraction(self, user_id: int, avatar_id: int) -> None:
        if self._memory_service is None or self._fact_trigger_service is None:
            return
        if not await self._fact_trigger_service.bump_and_should_trigger(user_id=user_id, avatar_id=avatar_id):
            return
        task = asyncio.create_task(self._run_fact_extraction(user_id=user_id, avatar_id=avatar_id))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    async def _run_fact_extraction(self, user_id: int, avatar_id: int) -> None:
        try:
            await self._memory_service.extract_facts(user_id=user_id, avatar_id=avatar_id)
        except Exception:
            logger.exception("Background fact extraction failed")

    async def _ensure_rate_limit(self, user_id: int) -> None:
        if self._llm_rate_limit_service is None:
            return
        allowed = await self._llm_rate_limit_service.allow_request(user_id)
        if not allowed:
            msg = "LLM request rate limit exceeded."
            raise LLMRateLimitExceededError(msg)
