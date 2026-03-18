from aiogram import Router

from server.apps.bot.handlers.callbacks import router as callbacks_router
from server.apps.bot.handlers.commands import router as commands_router
from server.apps.bot.handlers.dialog import router as dialog_router
from server.apps.bot.handlers.start import router as start_router

bot_router = Router(name="bot-root")
bot_router.include_router(start_router)
bot_router.include_router(commands_router)
bot_router.include_router(callbacks_router)
bot_router.include_router(dialog_router)

__all__ = [
    "bot_router",
]
