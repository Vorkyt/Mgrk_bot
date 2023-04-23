from typing import Any, Awaitable, Callable, Dict

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from ..protocols.telegram_user_event import TelegramUserEvent
from ..services.database.models import BotUser


class BotUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramUserEvent, Dict[str, Any]], Awaitable[Any]],
        event: TelegramUserEvent,
        data: Dict[str, Any],
    ) -> Any:
        from_user: types.User = event.from_user  # type: ignore

        bot_user, _ = await BotUser.get_or_create(
            dict(username=from_user.username, full_name=from_user.full_name),
            id=from_user.id,
        )

        data["bot_user"] = bot_user
        return await handler(event, data)
