from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.utils.keyboard import InlineKeyboardBuilder

if TYPE_CHECKING:
    from collections.abc import Sequence

    from aiogram.types import InlineKeyboardMarkup

    from server.apps.avatars.models.avatar import Avatar


def build_avatar_keyboard(avatars: Sequence[Avatar]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for avatar in avatars:
        builder.button(text=avatar.name, callback_data=f"avatar:{avatar.id}")
    builder.adjust(1) # кол-во кнопок в ряду
    return builder.as_markup()
