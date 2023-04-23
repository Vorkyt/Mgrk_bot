from aiogram import types
from aiogram.fsm.context import FSMContext
from bot.state import UserMenuState

from ... import markups
from ...bot import bot
from ...services.database.models import BotUser, ReplyMenu
from ..admin import reply_menu as admin_reply_menu
from . import router


async def send_user_reply_menu(bot_user: BotUser, reply_menu: ReplyMenu):
    await reply_menu.fetch_related("inline_menu")
    return await admin_reply_menu.send_reply_menu(
        bot_user,
        reply_menu,
        reply_menu.inline_menu,
        reply_markup=await markups.create_user_reply_menu_markup(reply_menu),
        inline_markup=await markups.create_user_inline_menu_markup(
            reply_menu.inline_menu
        ),
        text=reply_menu.inline_menu.text,
    )


@router.message(
    UserMenuState.waiting_action,
    admin_reply_menu.child_button_filter,
    admin_reply_menu.remove_messages,
)
async def child_button_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser, child: ReplyMenu
):
    await child.fetch_related("children", "parent", "inline_menu")

    if child.children:
        dialog_messages = await send_user_reply_menu(bot_user, child)
        return await state.update_data(dialog_messages=dialog_messages, menu=child)

    if child.parent:
        dialog_messages = await admin_reply_menu.send_reply_menu(
            bot_user,
            child.parent,
            child.inline_menu,
            reply_markup=await markups.create_user_reply_menu_markup(child.parent),
            inline_markup=await markups.create_user_inline_menu_markup(
                child.inline_menu
            ),
            text=child.inline_menu.text,
        )

        await state.update_data(dialog_messages=dialog_messages)


@router.message(
    UserMenuState.waiting_action,
    admin_reply_menu.back_button_filter,
    admin_reply_menu.remove_messages,
)
async def back_button_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]

    if menu.parent is None:
        return

    dialog_messages = await send_user_reply_menu(bot_user, menu.parent)
    await state.update_data(dialog_messages=dialog_messages, menu=menu.parent)
