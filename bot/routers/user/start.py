from aiogram import types
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext

from ...services.database.models import BotUser, ReplyMenu
from ...state import UserMenuState
from . import reply_menu, router


@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext, bot_user: BotUser):
    root_menu = await ReplyMenu.get_root_menu()
    dialog_messages = await reply_menu.send_user_reply_menu(bot_user, root_menu)
    await state.set_state(UserMenuState.waiting_action)
    await state.update_data(menu=root_menu, dialog_messages=dialog_messages)
