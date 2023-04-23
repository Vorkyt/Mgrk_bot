from aiogram import F, types
from aiogram.fsm.context import FSMContext

from ... import markups
from ...services.database.models import BotUser, InlineMenu, ReplyMenu
from ...state import UserMenuState
from ..admin import reply_menu as admin_reply_menu
from . import router


@router.callback_query(
    UserMenuState.waiting_action,
    markups.UserInlineMenuCallbackData.filter(
        F.type == markups.UserInlineMenuCallbackData.Type.child
    ),
    admin_reply_menu.remove_messages,
)
async def child_button_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    data = markups.UserInlineMenuCallbackData.unpack(query.data)  # type: ignore
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    child = await InlineMenu.filter(id=data.menu_id).prefetch_related("parent").first()

    if child is None:
        return

    dialog_messages = await admin_reply_menu.send_reply_menu(
        bot_user,
        menu,
        child,
        reply_markup=await markups.create_user_reply_menu_markup(menu),
        inline_markup=await markups.create_user_inline_menu_markup(child),
        text=child.text,
    )

    await state.update_data(dialog_messages=dialog_messages)
