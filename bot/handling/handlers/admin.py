import logging
import asyncio

from aiogram import Bot, Router, F
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

from bot.handling.states import MailingSG
from database import requests

logger = logging.getLogger(__name__)

admin_router = Router()


# Реагирует на нажатие кнопки рассылки
@admin_router.callback_query(F.data == "mailing")
async def click_mailing(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        text="Введите текст рассылки (до 1000 символов)",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back")]]
        ),
    )

    await state.set_state(MailingSG.send_mailing_text)


# Реагирует на кнопку назад в контексте ввода текста рассылки
@admin_router.callback_query(F.data == "back", StateFilter(MailingSG.send_mailing_text))
async def click_back_from_sending_mailing_text(
    callback: CallbackQuery, state: FSMContext
):
    await callback.answer()
    await callback.message.edit_text(
        text="Привет, админ!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Рассылка", callback_data="mailing")]
            ]
        ),
    )

    await state.clear()


# Реагирует на ввод текста рассылки
@admin_router.message(StateFilter(MailingSG.send_mailing_text))
async def mailing_text_sent(message: Message, state: FSMContext):
    await message.answer(
        text=f"Текст рассылки:\n<code>{message.text.strip()}</code>\n\n <b><i>Подтвердить??</i></b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
                [InlineKeyboardButton(text="Назад", callback_data="back")],
            ]
        ),
    )

    await state.update_data(mailing_text=message.text.strip())
    await state.set_state(MailingSG.confirm_mailing)


# Реагирует на кнопку назад в контексте подтверждения рассылки
@admin_router.callback_query(F.data == "back", StateFilter(MailingSG.confirm_mailing))
async def back_from_confirmation_mailing(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(
        text="Введите текст рассылки (до 1000 символов)",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back")]]
        ),
    )

    await state.set_state(MailingSG.send_mailing_text)


# Реагирует на подтверждение рассылки
@admin_router.callback_query(
    F.data == "confirm", StateFilter(MailingSG.confirm_mailing)
)
async def mailing_confirmed(
    callback: CallbackQuery, state: FSMContext, conn: AsyncConnection, bot: Bot
):
    state_data = await state.get_data()

    await callback.answer()
    await callback.message.edit_text(text="Рассылка подтверждена и начата!")
    await callback.message.answer(
        text="Привет, админ!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Рассылка", callback_data="mailing")]
            ]
        ),
    )

    await state.clear()

    mailing_text = state_data.get("mailing_text", "Тут должен был быть текст рассылки.")
    alive_users = await requests.users.get_all_alive_users(conn=conn)
    for recipient_row in alive_users:
        await bot.send_message(chat_id=recipient_row[0], text=mailing_text)
        await asyncio.sleep(0.05)
    logger.info("Рассылка завершена успешно!")
