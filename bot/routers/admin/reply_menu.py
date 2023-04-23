import asyncio
from typing import List, Optional, Union

from aiogram import F, types
from aiogram.fsm.context import FSMContext

from ... import markups
from ...bot import bot
from ...services.database.models import BotUser, InlineMenu, MessageFile, ReplyMenu
from ...state import (
    AddReplyMenuButtonState,
    AdminReplyMenuState,
    EditReplyBackButtonTextState,
    EditReplyButtonNameState,
)
from ...utils.enums import Alignment
from . import router


def decide_file_send_method(input_file: types.BufferedInputFile):
    filename: str = input_file.filename.lower()  # type: ignore

    if filename.endswith(".png") or filename.endswith(".jpg"):
        return bot.send_photo

    if filename.endswith(".gif"):
        return bot.send_animation

    if filename.endswith(".mp4"):
        return bot.send_video

    return bot.send_document


async def send_reply_menu(
    bot_user: BotUser,
    reply_menu: ReplyMenu,
    inline_menu: InlineMenu,
    *,
    reply_markup: types.ReplyKeyboardMarkup,
    inline_markup: Optional[types.InlineKeyboardMarkup] = None,
    text: Optional[str] = None,
):
    await inline_menu.fetch_related("file")

    message_text = (text or bot.phrases.admin.set_message_in_admin).format(
        bot_user=bot_user
    )

    if inline_markup is None:
        if inline_menu is None or inline_menu.file is None:
            return [
                await bot.send_message(
                    bot_user.id, message_text, reply_markup=reply_markup
                )
            ]

        input_file = types.BufferedInputFile(
            inline_menu.file.bytes, inline_menu.file.filename
        )

        send_method = decide_file_send_method(input_file)
        return [
            await send_method(
                bot_user.id, input_file, caption=message_text, reply_markup=reply_markup
            )
        ]

    reply_markup_message = await bot.send_message(
        bot_user.id,
        bot.phrases.loading_message.format(bot_user=bot_user),
        reply_markup=reply_markup,
    )

    if inline_menu and inline_menu.file:
        input_file = types.BufferedInputFile(
            inline_menu.file.bytes, inline_menu.file.filename
        )
        send_method = decide_file_send_method(input_file)
        inline_markup_message = await send_method(
            bot_user.id, input_file, caption=message_text, reply_markup=inline_markup
        )
    else:
        inline_markup_message = await bot.send_message(
            bot_user.id, message_text, reply_markup=inline_markup
        )

    return [inline_markup_message, reply_markup_message]


async def send_admin_reply_menu(bot_user: BotUser, reply_menu: ReplyMenu):
    await reply_menu.fetch_related("inline_menu")

    return await send_reply_menu(
        bot_user,
        reply_menu,
        reply_menu.inline_menu,
        reply_markup=await markups.create_admin_reply_menu_markup(reply_menu),
        inline_markup=await markups.create_admin_inline_menu_markup(
            reply_menu.inline_menu
        ),
        text=reply_menu.inline_menu.text,
    )


async def child_button_filter(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]

    for child in menu.children:
        if child.name == message.text:
            return {"child": child}

    return False


async def remove_messages(
    message_or_query: Union[types.Message, types.CallbackQuery], state: FSMContext
):
    state_data = await state.get_data()

    if isinstance(message_or_query, types.Message):
        messages: List[types.Message] = [message_or_query]
    else:
        messages: List[types.Message] = []

    if dialog_messages := state_data.get("dialog_messages"):
        messages.extend(dialog_messages)

    if messages:
        await asyncio.gather(
            *(bot.delete_message(m.chat.id, m.message_id) for m in messages),
            return_exceptions=True,
        )

    await state.update_data(dialog_messages=[])
    return True


async def back_button_filter(message: types.Message, state: FSMContext):
    if message.text == bot.phrases.back:
        return True

    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    return message.text == menu.back_button_text


@router.message(
    AdminReplyMenuState.waiting_action,
    F.text == bot.phrases.admin.add_button,
    remove_messages,
)
async def add_button_handler(message: types.Message, state: FSMContext):
    enter_name_message = await message.answer(bot.phrases.admin.enter_name)
    await state.set_state(AddReplyMenuButtonState.waiting_name)
    await state.update_data(dialog_messages=[enter_name_message])


@router.message(
    AdminReplyMenuState.waiting_action, F.text, child_button_filter, remove_messages
)
async def child_button_handler(
    message: types.Message, state: FSMContext, child: ReplyMenu, bot_user: BotUser
):
    dialog_messages = await send_admin_reply_menu(bot_user, child)
    state_data = await state.get_data()
    state_data["dialog_messages"].extend(dialog_messages)
    state_data["menu"] = child
    await state.set_data(state_data)


@router.message(AddReplyMenuButtonState.waiting_name, F.text, remove_messages)
async def add_button_text_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    inline_menu = await InlineMenu.create()
    await ReplyMenu.create(name=message.text, parent=menu, inline_menu=inline_menu)
    dialog_messages = await send_admin_reply_menu(bot_user, menu)
    await state.set_state(AdminReplyMenuState.waiting_action)
    await state.update_data(dialog_messages=dialog_messages)


@router.message(
    AdminReplyMenuState.waiting_action,
    F.text == bot.phrases.admin.remove_button,
    remove_messages,
)
async def remove_button_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]

    if menu.parent is None:
        return

    await menu.delete()
    dialog_messages = await send_admin_reply_menu(bot_user, menu.parent)
    await state.update_data(menu=menu.parent, dialog_messages=dialog_messages)


@router.message(AdminReplyMenuState.waiting_action, back_button_filter, remove_messages)
async def back_handler(message: types.Message, state: FSMContext, bot_user: BotUser):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]

    if menu.parent is None:
        return

    dialog_messages = await send_admin_reply_menu(bot_user, menu.parent)
    await state.update_data(menu=menu.parent, dialog_messages=dialog_messages)


@router.message(
    AdminReplyMenuState.waiting_action,
    F.text == bot.phrases.admin.buttons_horizontal,
    remove_messages,
)
async def buttons_horizontal_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    menu.alignment = Alignment.horizontal
    dialog_messages = await send_admin_reply_menu(bot_user, menu)
    await state.update_data(dialog_messages=dialog_messages)
    await menu.save()


@router.message(
    AdminReplyMenuState.waiting_action,
    F.text == bot.phrases.admin.buttons_vertical,
    remove_messages,
)
async def buttons_vertical_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    menu.alignment = Alignment.vertical
    dialog_messages = await send_admin_reply_menu(bot_user, menu)
    await state.update_data(dialog_messages=dialog_messages)
    await menu.save()


@router.message(
    AdminReplyMenuState.waiting_action,
    F.text == bot.phrases.admin.edit_back_button_text,
    remove_messages,
)
async def edit_back_button_text_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    enter_text_message = await bot.send_message(
        bot_user.id, bot.phrases.admin.enter_text
    )
    await state.set_state(EditReplyBackButtonTextState.waiting_text)
    await state.update_data(dialog_messages=[enter_text_message])


@router.message(EditReplyBackButtonTextState.waiting_text, F.text, remove_messages)
async def back_button_text_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    menu.back_button_text = message.text  # type: ignore
    dialog_messages = await send_admin_reply_menu(bot_user, menu)
    await state.set_state(AdminReplyMenuState.waiting_action)
    await state.update_data(dialog_messages=dialog_messages)
    await menu.save()


@router.message(
    AdminReplyMenuState.waiting_action,
    F.text == bot.phrases.admin.edit_name,
    remove_messages,
)
async def edit_name_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    enter_name_message = await bot.send_message(
        bot_user.id, bot.phrases.admin.enter_name
    )
    await state.set_state(EditReplyButtonNameState.waiting_name)
    await state.update_data(dialog_messages=[enter_name_message])


@router.message(EditReplyButtonNameState.waiting_name, F.text, remove_messages)
async def name_handler(message: types.Message, state: FSMContext, bot_user: BotUser):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    menu.name = message.text  # type: ignore
    await state.set_state(AdminReplyMenuState.waiting_action)
    dialog_messages = await send_admin_reply_menu(bot_user, menu)
    await state.update_data(dialog_messages=dialog_messages)
    await menu.save()
