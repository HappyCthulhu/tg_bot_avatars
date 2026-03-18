from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from django.conf import settings

if TYPE_CHECKING:
    from aiogram import Bot

    from llm import LLMService


class StreamingService:
    STREAM_EDIT_INTERVAL = settings.STREAM_EDIT_INTERVAL

    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def stream_reply(
        self,
        chat_id: int,
        messages: list[dict],
        llm_service: LLMService,
    ) -> str:
        telegram_message = await self._bot.send_message(chat_id=chat_id, text="...")
        message_id = telegram_message.message_id

        full_text = ""
        last_sent_text = "..."
        last_edit_ts = 0.0

        async for token in llm_service.stream_generate(messages):
            full_text += token
            now = time.monotonic()
            if now - last_edit_ts < self.STREAM_EDIT_INTERVAL:
                continue

            candidate_text = full_text.strip() or "..."
            if candidate_text == last_sent_text:
                continue

            await self._safe_edit_message(chat_id, message_id, candidate_text)
            last_sent_text = candidate_text
            last_edit_ts = now

        final_text = full_text.strip() or "..."
        if final_text != last_sent_text:
            await self._safe_edit_message(chat_id, message_id, final_text)

        return final_text

    async def _safe_edit_message(self, chat_id: int, message_id: int, text: str) -> None:
        try:
            await self._bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
            )
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after)
            await self._bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
            )
        except TelegramBadRequest:
            # Ignore non-critical edit errors like "message is not modified".
            return
