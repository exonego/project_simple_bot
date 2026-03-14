import logging
from collections.abc import Callable, Awaitable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Update, User
from psycopg import AsyncConnection

from database import requests
from bot.enums import Role

logger = logging.getLogger(__name__)


# Определяет роль пользвоателя и передает ее в контекст
class RoleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:

        user: User = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        admin_ids: list[int] = data.get("admin_ids")
        conn: AsyncConnection = data.get("conn")

        user_row: tuple = data.get("user_row")

        if user_row is None:

            if user.id not in admin_ids:
                data["role"] = Role.USER
                return await handler(event, data)
            else:
                data["role"] = Role.ADMIN
        else:

            if user_row[2] == Role.ADMIN and user.id not in admin_ids:
                await requests.users.change_role(
                    conn=conn, tg_id=user.id, role=Role.USER
                )
                data["role"] = Role.USER
            elif user_row[2] == Role.USER and user.id in admin_ids:
                await requests.users.change_role(
                    conn=conn, tg_id=user.id, role=Role.ADMIN
                )
                data["role"] = Role.ADMIN
            else:
                data["role"] = user_row[2]

        return await handler(event, data)
