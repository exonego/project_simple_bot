import logging

from psycopg import AsyncConnection

from bot.enums import Role


logger = logging.getLogger(__name__)


# Извлекает пользователя по tg_id
async def get_user(
    conn: AsyncConnection,
    *,
    tg_id: int,
) -> tuple | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                SELECT *
                FROM users
                WHERE tg_id = %s;
            """,
            params=(tg_id,),
        )
        row = await data.fetchone()
    logger.info(f"Row is {row}")
    return row if row else None


# Иззвлекает всех живых
async def get_all_alive_users(conn: AsyncConnection) -> list[tuple]:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                SELECT *
                FROM users
                WHERE is_alive = true;
            """
        )
        user_rows = await data.fetchall()
    logger.info("Все живые пользователи извлечены")
    return user_rows if user_rows else None


# Добавляет нового пользователя
async def add_user(
    conn: AsyncConnection, *, tg_id: int, role: Role = Role.USER, is_alive: bool = True
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                INSERT INTO users (tg_id, role, is_alive)
                VALUES (
                    %(tg_id)s,
                    %(role)s,
                    %(is_alive)s
                ) ON CONFLICT DO NOTHING;
            """,
            params={"tg_id": tg_id, "role": role, "is_alive": is_alive},
        )
    logger.info(
        f"Пользователь добавлен в users. tg_id={tg_id}, role={role}, is_alive={is_alive}"
    )


# Изменяет роль пользователя по user_id
async def change_role(
    conn: AsyncConnection,
    *,
    role: Role,
    tg_id: int,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                UPDATE users
                SET role = %s
                WHERE tg_id = %s;
            """,
            params=(role, tg_id),
        )
    logger.info(f"Роль изменена на {role} для пользователя {tg_id}")


# Изменяет is_alive пользователя по id
async def change_is_alive(conn: AsyncConnection, *, is_alive: bool, tg_id: int) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                UPDATE users
                SET is_alive = %s
                WHERE tg_id = %s;
            """,
            params=(is_alive, tg_id),
        )
    logger.info(f"Статус is_alive = {is_alive} для пользователя {tg_id}")


# Изменяет имя пользователя по user_id
async def change_name(
    conn: AsyncConnection,
    *,
    name: str,
    tg_id: int,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                UPDATE users
                SET name = %s
                WHERE tg_id = %s;
            """,
            params=(name, tg_id),
        )
    logger.info(f"Имя изменено на {name} для пользователя {tg_id}")
