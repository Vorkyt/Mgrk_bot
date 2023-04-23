from aiogram.fsm.state import State, StatesGroup


class AdminReplyMenuState(StatesGroup):
    waiting_action = State()


class AddReplyMenuButtonState(StatesGroup):
    waiting_name = State()


class AddInlineMenuButtonState(StatesGroup):
    waiting_name = State()


class AddUrlButtonState(StatesGroup):
    waiting_name = State()
    waiting_url = State()


class RemoveUrlButtonState(StatesGroup):
    waiting_url = State()


class EditFileState(StatesGroup):
    waiting_file = State()


class EditTextState(StatesGroup):
    waiting_text = State()


class EditBackButtonTextState(StatesGroup):
    waiting_text = State()


class EditReplyBackButtonTextState(StatesGroup):
    waiting_text = State()


class UserMenuState(StatesGroup):
    waiting_action = State()


class EditNameState(StatesGroup):
    waiting_name = State()


class EditReplyButtonNameState(StatesGroup):
    waiting_name = State()
