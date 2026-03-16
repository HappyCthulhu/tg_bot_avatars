from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async

from server.apps.avatars.models import Avatar
from server.apps.bot.services import TelegramUserService
from server.apps.bot.states import DialogStates

router = Router(name="bot-callbacks")


@router.callback_query(F.data.startswith("avatar:"))
async def avatar_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user is None or callback.data is None:
        await callback.answer()
        return

    avatar_id_raw = callback.data.replace("avatar:", "", 1)
    if not avatar_id_raw.isdigit():
        await callback.answer("Некорректный аватар", show_alert=True)
        return
    avatar_id = int(avatar_id_raw)

    avatar = await sync_to_async(Avatar.objects.filter(id=avatar_id).first)()
    if avatar is None:
        await callback.answer("Аватар не найден", show_alert=True)
        return

    telegram_user_service = TelegramUserService()
    user = await telegram_user_service.get_or_create_user(callback.from_user)
    user.active_avatar = avatar
    await sync_to_async(user.save)(update_fields=["active_avatar", "updated_at"])

    if callback.message is not None:
        await callback.message.answer(f"Выбран аватар: {avatar.name}. Можешь писать сообщение.")
    await callback.answer()
    await state.set_state(DialogStates.dialog)
