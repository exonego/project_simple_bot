import logging

from aiogram import Router
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from psycopg import AsyncConnection

from bot.enums import Role
from bot.handling.states import ChangeNameSG, MailingSG
from database import requests

logger = logging.getLogger(__name__)

start_router = Router()


@start_router.message(CommandStart())
async def start_cmd(
    message: Message,
    conn: AsyncConnection,
    user_row: tuple | None,
    role: Role,
    state: FSMContext,
) -> None:
    """Обрабатывает команду /start"""

    if user_row is None:
        await message.answer(text="Добро пожаловать в бота! Введи свое имя.")

        await requests.users.add_user(
            conn=conn, tg_id=message.from_user.id, role=role, is_alive=True
        )

        await state.set_state(ChangeNameSG.send_name)

    else:
        if role == Role.USER:
            if user_row[1] is not None:
                await message.answer(
                    text=f"Добро пожаловать, {user_row[1]}!",
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(
                                    text="Изменить имя", callback_data="change_name"
                                )
                            ]
                        ]
                    ),
                )
            else:
                await message.answer(text="Добро пожаловать в бота! Введи свое имя.")

                await state.set_state(ChangeNameSG.send_name)

        elif role == Role.ADMIN:
            await message.answer(
                text="Привет, админ!",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="Рассылка", callback_data="mailing")]
                    ]
                ),
            )

        await requests.users.change_is_alive(
            conn=conn, is_alive=True, tg_id=message.from_user.id
        )
