import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import psycopg_pool

from bot.handling.handlers.start import start_router
from bot.handling.handlers.user import user_router

# from app.bot.handlers.admin import admin_router
from bot.handling.middlewares import DBConnMiddleware, UserRowMiddleware, RoleMiddleware
from database import get_pg_pool
from config.config import Config

logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main(config: Config) -> None:
    logger.info("Старт бота")
    # Инициализация бота и диспетчера
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Создание пула соединений с Postgres
    db_pool: psycopg_pool.AsyncConnectionPool = await get_pg_pool(
        db_name=config.db.name,
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
    )

    # Регистрация роутеров
    logger.info("Регистрация роутеров...")
    dp.include_routers(start_router, user_router)
    # Регистрация миддлварей
    logger.info("Регистрация миддлварей...")
    dp.update.outer_middleware(DBConnMiddleware())
    dp.update.outer_middleware(UserRowMiddleware())
    dp.update.outer_middleware(RoleMiddleware())

    # Запуск поллинга
    try:
        await dp.start_polling(
            bot,
            db_pool=db_pool,
            admin_ids=config.bot.admin_ids,
        )
    except Exception as e:
        logger.exception(e)
    finally:
        # Закрытие пула соединений
        await db_pool.close()
        logger.info("Соединение с Postgres прервано")
