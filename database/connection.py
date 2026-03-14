import logging
from urllib.parse import quote

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)


# Функция, возвращающая безопасную строку conninfo для подключения к PostrgeSQL
def build_pg_conninfo(
    db_name: str,
    host: str,
    port: int,
    user: str,
    password: str,
) -> str:
    conninfo = (
        f"postgresql://{quote(user, safe='')}:{quote(password, safe='')}"
        f"@{host}:{port}/{db_name}"
    )
    logger.debug(
        f"Создание строки подключения к PostgreSQL (пароль не указан): "
        f"postgresql://{quote(user, safe='')}@{host}:{port}/{db_name}"
    )
    return conninfo


# Функция, логирующая версию СУБД, к которой происходит подключение
async def log_db_version(connection: AsyncConnection) -> None:
    try:
        async with connection.cursor() as cursor:
            await cursor.execute("SELECT version();")
            db_version = await cursor.fetchone()
            logger.info(f"Подключился к PostrgeSQL версии: {db_version[0]}")
    except Exception as e:
        logger.warning(f"Не удалось извлечь версию БД: {e}")


# Функция, возвращающая открытое соединение с PostgreSQL
async def get_pg_connection(
    db_name: str, host: str, port: int, user: str, password: str
) -> AsyncConnection:
    conninfo = build_pg_conninfo(db_name, host, port, user, password)
    connection: AsyncConnection | None = None

    try:
        connection = await AsyncConnection.connect(conninfo=conninfo)
        await log_db_version(connection)
        return connection
    except Exception as e:
        logger.exception(f"Не удалось подключиться к PostgreSQL {e}")
        if connection:
            await connection.close()
        raise


# Функция, возвращающая пул соединений с PostgreSQL
async def get_pg_pool(
    db_name: str,
    host: str,
    port: int,
    user: str,
    password: str,
    min_size: int = 2,
    max_size: int = 5,
    timeout: float | None = 10.0,
) -> AsyncConnectionPool:
    conninfo = build_pg_conninfo(db_name, host, port, user, password)
    db_pool: AsyncConnectionPool | None = None

    try:
        db_pool = AsyncConnectionPool(
            conninfo=conninfo,
            min_size=min_size,
            max_size=max_size,
            timeout=timeout,
            open=False,
        )

        await db_pool.open()

        async with db_pool.connection() as connection:
            await log_db_version(connection)

        return db_pool
    except Exception as e:
        logger.exception(
            f"Не удалось инициализировать пул соединений для PostgreSQL: {e}"
        )
        if db_pool and not db_pool.closed:
            await db_pool.close()
        raise
