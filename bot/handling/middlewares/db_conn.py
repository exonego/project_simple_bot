import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Update
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)


# Передает соединение с БД в контекст
class DBConnMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        db_pool: AsyncConnectionPool = data.get("db_pool")

        if db_pool is None:
            logger.error("Пул соединений с БД не представлен в контексте миддлвари")
            raise RuntimeError("Отсутствует пул соединений с БД в контексте миддлвари")

        async with db_pool.connection() as connection:
            try:
                async with connection.transaction():
                    data["conn"] = connection
                    return await handler(event, data)
            except Exception as e:
                logger.exception(f"Транзакция была отменена из-за ошибки: {e}")
                raise
