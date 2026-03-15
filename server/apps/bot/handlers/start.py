from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async

from server.apps.avatars.models import Avatar
from server.apps.bot.keyboards import build_avatar_keyboard
from server.apps.bot.services import TelegramUserService
from server.apps.bot.states import DialogStates

router = Router(name="bot-start")


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return

    telegram_user_service = TelegramUserService()
    await telegram_user_service.get_or_create_user(message.from_user)

    avatars = await sync_to_async(list)(Avatar.objects.all().order_by("id"))
    if not avatars:
        await message.answer("Аватары пока не настроены.")
        await state.clear()
        return

    await message.answer(
        "Выбери аватара для общения",
        reply_markup=build_avatar_keyboard(avatars),
    )
    await state.set_state(DialogStates.choosing_avatar)
