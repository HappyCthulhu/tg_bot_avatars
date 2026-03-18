import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async
from django.conf import settings
from loguru import logger

from llm import LLMService, PromptBuilder
from providers import RedisProvider
from server.apps.bot.services import TelegramUserService
from server.apps.bot.states import DialogStates
from server.apps.users.models import User
from services import DialogService, FactTriggerService, MemoryService, ShortMemoryService, StreamingService

router = Router(name="bot-dialog")


@router.message(DialogStates.dialog, F.text)
async def dialog_message_handler(message: Message, state: FSMContext) -> None:
    if message.from_user is None or message.text is None:
        return

    telegram_user_service = TelegramUserService()
    user = await telegram_user_service.get_or_create_user(message.from_user)
    user = await sync_to_async(User.objects.select_related("active_avatar").get)(id=user.id)

    if user.active_avatar is None:
        await message.answer("Сначала выбери аватара через /start.")
        await state.set_state(DialogStates.choosing_avatar)
        return

    bot = message.bot
    redis_provider = RedisProvider()
    llm_service = LLMService()
    prompt_builder = PromptBuilder()
    short_memory_service = ShortMemoryService(redis_provider=redis_provider)
    memory_service = MemoryService(
        short_memory_service=short_memory_service,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )
    fact_trigger_service = FactTriggerService(
        redis_provider=redis_provider,
        interval=settings.FACT_TRIGGER_INTERVAL,
    )
    dialog_service = DialogService(
        short_memory_service=short_memory_service,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
        memory_service=memory_service,
        fact_trigger_service=fact_trigger_service,
        streaming_service=StreamingService(bot=bot),
    )

    stop_typing = asyncio.Event()

    async def _typing_loop() -> None:
        while not stop_typing.is_set():
            await bot.send_chat_action(chat_id=message.chat.id, action="typing")
            try:
                await asyncio.wait_for(stop_typing.wait(), timeout=4)
            except TimeoutError:
                continue

    typing_task = asyncio.create_task(_typing_loop())
    try:
        await dialog_service.handle_user_message_stream(
            user=user,
            avatar=user.active_avatar,
            text=message.text,
            chat_id=message.chat.id,
        )
    except Exception as exc:
        logger.exception("Error handling user message stream", exc_info=exc)
        await message.answer("ИИ сейчас перегружен. Попробуй позже.")
    finally:
        stop_typing.set()
        await typing_task
