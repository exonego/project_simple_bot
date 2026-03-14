from aiogram.fsm.state import State, StatesGroup


class ChangeNameSG(StatesGroup):
    send_name = State()


class MailingSG(StatesGroup):
    send_mailing_text = State()
    confirm_mailing = State()
