from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async

from llm import LLMService, PromptBuilder
from providers import RedisProvider
from server.apps.avatars.models import Avatar
from server.apps.bot.keyboards import build_avatar_keyboard
from server.apps.bot.services import TelegramUserService
from server.apps.bot.states import DialogStates
from server.apps.users.models import User
from services import MemoryService, ShortMemoryService

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import (
        Message,
        User as AiogramUser,
    )

router = Router(name="bot-commands")


async def _get_user_with_avatar(telegram_user: AiogramUser) -> User:
    telegram_user_service = TelegramUserService()
    user = await telegram_user_service.get_or_create_user(telegram_user)
    return await sync_to_async(User.objects.select_related("active_avatar").get)(id=user.id)


@router.message(Command("history"))
async def history_handler(message: Message) -> None:
    if message.from_user is None:
        return
    user = await _get_user_with_avatar(message.from_user)
    if user.active_avatar is None or not user.active_avatar.active:
        await message.answer("Сначала выбери аватара через /start.")
        return

    short_memory_service = ShortMemoryService(redis_provider=RedisProvider())
    history_messages = await short_memory_service.get_messages(user.id, user.active_avatar.id)
    if not history_messages:
        await message.answer("История диалога пуста.")
        return

    formatted = "\n".join(
        f"{'User' if item.sender == 'user' else 'Assistant'}: {item.text}" for item in history_messages[-10:]
    )
    await message.answer(formatted)


@router.message(Command("facts"))
async def facts_handler(message: Message) -> None:
    if message.from_user is None:
        return
    user = await _get_user_with_avatar(message.from_user)
    if user.active_avatar is None or not user.active_avatar.active:
        await message.answer("Сначала выбери аватара через /start.")
        return

    memory_service = MemoryService(
        short_memory_service=ShortMemoryService(redis_provider=RedisProvider()),
        prompt_builder=PromptBuilder(),
        llm_service=LLMService(),
    )
    facts = await memory_service.get_facts_for_prompt(user.id, user.active_avatar.id)
    if not facts:
        await message.answer("Пока нет сохраненных фактов.")
        return
    await message.answer("\n".join(f"- {fact}" for fact in facts))


@router.message(Command("reset"))
async def reset_handler(message: Message) -> None:
    if message.from_user is None:
        return
    user = await _get_user_with_avatar(message.from_user)
    if user.active_avatar is None or not user.active_avatar.active:
        await message.answer("Сначала выбери аватара через /start.")
        return

    short_memory_service = ShortMemoryService(redis_provider=RedisProvider())
    await short_memory_service.clear_dialog(user.id, user.active_avatar.id)
    await message.answer("Контекст диалога очищен.")


@router.message(Command("change_avatar"))
async def change_avatar_handler(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    await _get_user_with_avatar(message.from_user)
    avatars = await sync_to_async(list)(Avatar.objects.filter(active=True).order_by("id"))
    if not avatars:
        await message.answer("Нет доступных активных аватаров.")
        await state.clear()
        return
    await message.answer(
        "Выбери аватара для общения",
        reply_markup=build_avatar_keyboard(avatars),
    )
    await state.set_state(DialogStates.choosing_avatar)


@router.message(Command("dialog"))
async def dialog_mode_handler(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    user = await _get_user_with_avatar(message.from_user)
    if user.active_avatar is None or not user.active_avatar.active:
        await message.answer("Сначала выбери аватара через /start.")
        await state.set_state(DialogStates.choosing_avatar)
        return
    await state.set_state(DialogStates.dialog)
    await message.answer("Режим диалога активирован. Можешь писать сообщение.")
