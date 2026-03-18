from __future__ import annotations

from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async

from server.apps.memory.models import MemoryFact

if TYPE_CHECKING:
    from llm import LLMService, PromptBuilder
    from services.short_memory_service import ShortMemoryService


class MemoryService:
    def __init__(
        self,
        short_memory_service: ShortMemoryService,
        prompt_builder: PromptBuilder,
        llm_service: LLMService,
    ) -> None:
        self._short_memory_service = short_memory_service
        self._prompt_builder = prompt_builder
        self._llm_service = llm_service

    async def get_facts_for_prompt(self, user_id: int, avatar_id: int) -> list[str]:
        queryset = MemoryFact.objects.filter(user_id=user_id, avatar_id=avatar_id).order_by("-created_at")
        return await sync_to_async(list)(queryset.values_list("text", flat=True))

    async def save_facts(self, user_id: int, avatar_id: int, facts: list[str]) -> None:
        normalized = [fact.strip() for fact in facts if fact and fact.strip()]
        if not normalized:
            return
        objects = [MemoryFact(user_id=user_id, avatar_id=avatar_id, text=fact) for fact in normalized]
        await sync_to_async(MemoryFact.objects.bulk_create)(objects)

    async def extract_facts(self, user_id: int, avatar_id: int) -> list[str]:
        dialog_messages = await self._short_memory_service.get_messages(user_id=user_id, avatar_id=avatar_id)
        if not dialog_messages:
            return []
        prompt = self._prompt_builder.build_fact_extraction_prompt(dialog_messages)
        facts = await self._llm_service.extract_facts(prompt)
        await self.save_facts(user_id=user_id, avatar_id=avatar_id, facts=facts)
        return facts
