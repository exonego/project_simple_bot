import logging

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatMemberUpdated,
)
from aiogram.filters import StateFilter, ChatMemberUpdatedFilter, KICKED
from aiogram.fsm.context import FSMContext
from psycopg import AsyncConnection

from bot.enums import Role
from bot.handling.states import ChangeNameSG, MailingSG
from database import requests

logger = logging.getLogger(__name__)

user_router = Router()


# Реагирует на нажатие кнопки смены имени
@user_router.callback_query(F.data == "change_name")
async def click_change_name(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        text="Введи свое имя.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back")]]
        ),
    )

    await state.set_state(ChangeNameSG.send_name)


# Реагирует на кнопку назад в контексте ввода имени
@user_router.callback_query(F.data == "back", StateFilter(ChangeNameSG.send_name))
async def back_from_sending_name(
    callback: CallbackQuery, state: FSMContext, user_row: tuple
):
    await callback.answer()

    if user_row[1]:
        await callback.message.edit_text(
            text=f"Добро пожаловать, {callback.message.text.strip()}!",
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

        await state.clear()
    else:
        await callback.message.answer(
            "Ты как вообще на эту кнопку нажал?"
            " Взаимодействовать с ботом через URL-запросы неправильно!"
            " Давай вводи имя."
        )


# Реагирует на ввод имени
@user_router.message(StateFilter(ChangeNameSG.send_name))
async def name_sent(message: Message, conn: AsyncConnection, state: FSMContext):
    await message.answer(text=f"Твое новое имя: {message.text.strip()}")
    await message.answer(
        text=f"Добро пожаловать, {message.text.strip()}!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Изменить имя", callback_data="change_name")]
            ]
        ),
    )

    await requests.users.change_name(
        conn=conn, name=message.text.strip(), tg_id=message.from_user.id
    )

    await state.clear()


# Реагирует на блокировку бота юзером
@user_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated, conn: AsyncConnection):
    logger.info(f"Пользователь {event.from_user.id} заблокировал бота")
    await requests.users.change_is_alive(
        conn, is_alive=False, user_id=event.from_user.id
    )


# Реагирует на любое сообщение
@user_router.message()
async def any_message(message: Message):
    await message.answer("Я тут!")
