from __future__ import annotations

from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from django.db import IntegrityError

from server.apps.bot.models import TelegramUser
from server.apps.users.models import User

if TYPE_CHECKING:
    from aiogram.types import User as AiogramUser


class TelegramUserService:
    async def get_or_create_user(self, aiogram_user: AiogramUser) -> User:
        telegram_profile = await sync_to_async(
            TelegramUser.objects.select_related("user").filter(telegram_id=aiogram_user.id).first,
        )()

        if telegram_profile is None:
            user = await sync_to_async(User.objects.create)()
            try:
                telegram_profile = await sync_to_async(TelegramUser.objects.create)(
                    user=user,
                    telegram_id=aiogram_user.id,
                )
            except IntegrityError:
                # Concurrent insert safety: another worker created this profile.
                telegram_profile = await sync_to_async(
                    TelegramUser.objects.select_related("user").get,
                )(telegram_id=aiogram_user.id)
                user = telegram_profile.user
        else:
            user = telegram_profile.user

        await self._sync_profile_fields(telegram_profile, aiogram_user, user)
        return user

    async def _sync_profile_fields(
        self,
        profile: TelegramUser,
        aiogram_user: AiogramUser,
        user: User,
    ) -> None:
        fields_to_update: list[str] = []

        first_name = aiogram_user.first_name or ""
        last_name = aiogram_user.last_name or ""
        language_code = aiogram_user.language_code or ""
        username = aiogram_user.username or ""
        is_premium = bool(getattr(aiogram_user, "is_premium", False))

        if profile.user_id != user.id:
            profile.user = user
            fields_to_update.append("user")

        if profile.first_name != first_name:
            profile.first_name = first_name
            fields_to_update.append("first_name")
        if profile.last_name != last_name:
            profile.last_name = last_name
            fields_to_update.append("last_name")
        if profile.language_code != language_code:
            profile.language_code = language_code
            fields_to_update.append("language_code")
        if profile.username != username:
            profile.username = username
            fields_to_update.append("username")
        if profile.is_premium != is_premium:
            profile.is_premium = is_premium
            fields_to_update.append("is_premium")

        if fields_to_update:
            await sync_to_async(profile.save)(update_fields=[*fields_to_update, "updated_at"])
