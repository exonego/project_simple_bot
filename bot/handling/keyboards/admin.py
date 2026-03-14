from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_admin_menu_kbd() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Рассылка", callback_data="mailing")]
        ]
    )


def get_confirm_kbd() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Подтвердить", callback_data="confirm")],
            [InlineKeyboardButton(text="Назад", callback_data="back")],
        ]
    )
