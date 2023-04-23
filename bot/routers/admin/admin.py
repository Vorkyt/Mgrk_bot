from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from ...services.database.models import BotUser, ReplyMenu
from ...state import AdminReplyMenuState
from . import reply_menu, router


@router.message(Command("admin"))
async def admin_command_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    root_menu = await ReplyMenu.get_root_menu()
    dialog_messages = await reply_menu.send_admin_reply_menu(bot_user, root_menu)
    await state.set_state(AdminReplyMenuState.waiting_action)
    await state.update_data(menu=root_menu, dialog_messages=dialog_messages)
