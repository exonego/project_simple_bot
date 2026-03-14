from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_user_menu_kbd() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить имя", callback_data="change_name")]
        ]
    )


def get_back_kbd() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back")]]
    )
