import logging
import os
from dataclasses import dataclass

from environs import Env

logger = logging.getLogger(__name__)


@dataclass
class BotSettings:
    token: str
    admin_ids: list[int]


@dataclass
class DBSettings:
    name: str
    host: str
    port: int
    user: str
    password: str


@dataclass
class LogSettings:
    level: str
    format: str
    style: str


@dataclass
class Config:
    bot: BotSettings
    db: DBSettings
    log: LogSettings


def load_config(path: str | None = None) -> Config:
    env = Env()

    if path:
        if not os.path.exists(path):
            logger.warning(f"Файл .env не найден по пути '{path}'")
        else:
            logger.info(f"Загрузка файла .env из '{path}'")
    env.read_env(path)

    token = env("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN не должна быть пустой")

    raw_ids = env.list("ADMIN_IDS", default=[])
    try:
        admin_ids = [int(i) for i in raw_ids]
    except ValueError as e:
        raise ValueError(f"ADMIN_IDS должны быть числами, получено: {raw_ids}") from e

    db = DBSettings(
        name=env("POSTGRES_DB"),
        host=env("POSTGRES_HOST"),
        port=env.int("POSTGRES_PORT"),
        user=env("POSTGRES_USER"),
        password=env("POSTGRES_PASSWORD"),
    )

    log_settings = LogSettings(
        level=env("LOG_LEVEL"), format=env("LOG_FORMAT"), style=env("LOG_STYLE")
    )

    logger.info("Конфигурация загружена успешно")
    return Config(
        bot=BotSettings(token=token, admin_ids=admin_ids),
        db=db,
        log=log_settings,
    )
