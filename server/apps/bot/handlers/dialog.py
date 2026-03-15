from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from asgiref.sync import sync_to_async

from server.apps.bot.services import TelegramUserService
from server.apps.bot.states import DialogStates
from server.apps.llm.simple_llm import generate_reply
from server.apps.users.models import User

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

    prompt_messages = [
        {"role": "system", "content": user.active_avatar.system_prompt},
        {"role": "user", "content": message.text},
    ]
    reply = await generate_reply(prompt_messages)
    await message.answer(reply)
