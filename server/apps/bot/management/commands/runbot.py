from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from server.apps.bot.handlers import bot_router


class Command(BaseCommand):
    help = "Run Telegram bot polling loop."

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        asyncio.run(self._run())

    async def _run(self) -> None:
        token = settings.BOT_TOKEN
        if not token:
            raise CommandError("BOT_TOKEN environment variable is required.")

        bot = Bot(token=token)
        dispatcher = Dispatcher(storage=MemoryStorage())
        dispatcher.include_router(bot_router)

        try:
            await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())
        finally:
            await bot.session.close()
