import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, User
from psycopg import AsyncConnection

from database import requests

logger = logging.getLogger(__name__)


# Передает строку пользователя в контекст
class UserRowMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")

        if user is None:
            return await handler(event, data)

        conn: AsyncConnection = data.get("conn")
        if conn is None:
            logger.error("Соединение с БД не найдено в контексте миддлвари")
            raise RuntimeError(
                "Отсутствует соединение с БД для извлечения строки пользователя"
            )

        user_row = await requests.users.get_user(conn, tg_id=user.id)
        data["user_row"] = user_row

        return await handler(event, data)
