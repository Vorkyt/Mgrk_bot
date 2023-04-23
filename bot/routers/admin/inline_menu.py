from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from aiogram import F, types
from aiogram.fsm.context import FSMContext

from ... import markups
from ...bot import bot
from ...services.database.models import BotUser, InlineMenu, MessageFile, ReplyMenu
from ...state import (
    AddInlineMenuButtonState,
    AddUrlButtonState,
    AdminReplyMenuState,
    EditBackButtonTextState,
    EditFileState,
    EditNameState,
    EditTextState,
    RemoveUrlButtonState,
)
from ...utils.enums import Alignment
from . import reply_menu, router


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.add_button
    ),
    reply_menu.remove_messages,
)
async def add_button_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore
    enter_button_name_message = await bot.send_message(
        query.from_user.id, bot.phrases.admin.enter_name
    )
    await state.set_state(AddInlineMenuButtonState.waiting_name)
    await state.update_data(
        dialog_messages=[enter_button_name_message], inline_menu_id=data.menu_id
    )


@router.message(
    AddInlineMenuButtonState.waiting_name, F.text, reply_menu.remove_messages
)
async def button_name_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]

    await InlineMenu.create(name=message.text, parent_id=state_data["inline_menu_id"])
    parent = await InlineMenu.get(id=state_data["inline_menu_id"])

    dialog_messages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        parent,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(parent),
        text=parent.text,
    )

    await state.update_data(dialog_messages=dialog_messages)
    await state.set_state(AdminReplyMenuState.waiting_action)


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.child
    ),
    reply_menu.remove_messages,
)
async def child_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore
    child = await InlineMenu.get(id=data.menu_id)

    dialog_messages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        child,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(child),
        text=child.text,
    )

    await state.update_data(dialog_messages=dialog_messages)


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.remove_button
    ),
    reply_menu.remove_messages,
)
async def remove_button_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore
    inline_menu = (
        await InlineMenu.filter(id=data.menu_id).prefetch_related("parent").first()
    )

    if inline_menu is None or inline_menu.parent is None:
        return

    await inline_menu.delete()

    dialog_messages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        inline_menu,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(inline_menu.parent),
        text=inline_menu.parent.text,
    )

    await state.update_data(dialog_messages=dialog_messages)


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.horizontal_alignment
    ),
    reply_menu.remove_messages,
)
async def horizontal_alignment_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore
    inline_menu = await InlineMenu.get(id=data.menu_id)
    inline_menu.alignment = Alignment.horizontal

    dialog_messages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        inline_menu,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(inline_menu),
        text=inline_menu.text,
    )

    await inline_menu.save()
    await state.update_data(dialog_messages=dialog_messages)


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.vertical_alignment
    ),
    reply_menu.remove_messages,
)
async def vertical_alignment_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore
    inline_menu = await InlineMenu.get(id=data.menu_id)
    inline_menu.alignment = Alignment.vertical

    dialog_messages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        inline_menu,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(inline_menu),
        text=inline_menu.text,
    )

    await inline_menu.save()
    await state.update_data(dialog_messages=dialog_messages)


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.add_url_button
    ),
    reply_menu.remove_messages,
)
async def add_url_button_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore
    enter_name_message = await bot.send_message(
        bot_user.id, bot.phrases.admin.enter_name
    )
    await state.set_state(AddUrlButtonState.waiting_name)
    await state.update_data(
        dialog_messages=[enter_name_message], inline_menu_id=data.menu_id
    )


@router.message(AddUrlButtonState.waiting_name, F.text, reply_menu.remove_messages)
async def url_button_name_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    enter_url_message = await bot.send_message(bot_user.id, bot.phrases.admin.enter_url)
    await state.set_state(AddUrlButtonState.waiting_url)
    await state.update_data(
        dialog_messages=[message, enter_url_message], name=message.text
    )


@router.message(
    AddUrlButtonState.waiting_url, F.text.startswith("http"), reply_menu.remove_messages
)
async def url_handler(message: types.Message, state: FSMContext, bot_user: BotUser):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    parent = await InlineMenu.get(id=state_data["inline_menu_id"])
    await InlineMenu.create(parent=parent, url=message.text, name=state_data["name"])

    dialog_messages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        parent,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(parent),
        text=parent.text,
    )

    await state.update_data(dialog_messages=dialog_messages)
    await state.set_state(AdminReplyMenuState.waiting_action)


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.remove_url_button
    ),
    reply_menu.remove_messages,
)
async def remove_url_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore
    enter_url_message = await bot.send_message(bot_user.id, bot.phrases.admin.enter_url)
    await state.set_state(RemoveUrlButtonState.waiting_url)
    await state.update_data(
        dialog_messages=[enter_url_message], inline_menu_id=data.menu_id
    )


@router.message(
    RemoveUrlButtonState.waiting_url,
    F.text.startswith("http"),
    reply_menu.remove_messages,
)
async def url_remove_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    inline_menu = await InlineMenu.get(id=state_data["inline_menu_id"])
    menu: ReplyMenu = state_data["menu"]
    await InlineMenu.filter(url=message.text, parent=inline_menu).delete()

    dialog_messages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        inline_menu,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(inline_menu),
        text=inline_menu.text,
    )

    await state.update_data(dialog_messages=dialog_messages)
    await state.set_state(AdminReplyMenuState.waiting_action)


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.edit_file
    ),
    reply_menu.remove_messages,
)
async def edit_file_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore

    enter_file_message = await bot.send_message(
        bot_user.id, bot.phrases.admin.enter_file
    )

    await state.set_state(EditFileState.waiting_file)
    await state.update_data(
        dialog_messages=[enter_file_message], inline_menu_id=data.menu_id
    )


@router.message(
    EditFileState.waiting_file,
    F.document | F.photo | F.video | F.animation,
    reply_menu.remove_messages,
)
async def file_handler(message: types.Message, state: FSMContext, bot_user: BotUser):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]

    inline_menu = (
        await InlineMenu.filter(id=state_data["inline_menu_id"])
        .prefetch_related("file")
        .first()
    )

    if inline_menu is None:
        return

    if inline_menu.file is not None:
        await inline_menu.file.delete()

    if message.content_type == "document":
        attachment = message.document
    elif message.content_type == "video":
        attachment = message.video
    elif message.content_type == "photo":
        attachment = message.photo[-1]  # type: ignore
    elif message.content_type == "animation":
        attachment = message.animation
    else:
        raise Exception("Unsupported content type")

    if attachment is not None:
        file = await bot.get_file(attachment.file_id)
        file_buffer: BinaryIO = await bot.download(attachment)  # type: ignore
        file_buffer.seek(0)

        filepath = Path(file.file_path)  # type: ignore

        await MessageFile.create(
            filename=filepath.name,
            bytes=file_buffer.read(),
            inline_menu=inline_menu,
        )

    dialog_messages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        inline_menu,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(inline_menu),
        text=inline_menu.text,
    )

    await state.update_data(dialog_messages=dialog_messages)
    await state.set_state(AdminReplyMenuState.waiting_action)


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.remove_file
    ),
    reply_menu.remove_messages,
)
async def remove_file_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    inline_menu = await InlineMenu.get(id=data.menu_id)
    await MessageFile.filter(inline_menu=inline_menu).delete()

    dialog_messages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        inline_menu,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(inline_menu),
        text=inline_menu.text,
    )

    await state.update_data(dialog_messages=dialog_messages)


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.edit_text
    ),
    reply_menu.remove_messages,
)
async def edit_text_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore
    enter_text_message = await bot.send_message(
        bot_user.id, bot.phrases.admin.enter_text
    )
    await state.set_state(EditTextState.waiting_text)
    await state.update_data(
        dialog_messages=[enter_text_message], inline_menu_id=data.menu_id
    )


@router.message(EditTextState.waiting_text, F.text, reply_menu.remove_messages)
async def text_handler(message: types.Message, state: FSMContext, bot_user: BotUser):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    inline_menu = await InlineMenu.get(id=state_data["inline_menu_id"])
    inline_menu.text = message.html_text  # type: ignore
    await inline_menu.save()

    dialog_messages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        inline_menu,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(inline_menu),
        text=inline_menu.text,
    )

    await state.set_state(AdminReplyMenuState.waiting_action)
    await state.update_data(dialog_messages=dialog_messages)


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.edit_back_button_text
    ),
    reply_menu.remove_messages,
)
async def edit_back_button_text_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore
    enter_text_message = await bot.send_message(
        bot_user.id, bot.phrases.admin.enter_text
    )
    await state.set_state(EditBackButtonTextState.waiting_text)
    await state.update_data(
        dialog_messages=[enter_text_message], inline_menu_id=data.menu_id
    )


@router.message(
    EditBackButtonTextState.waiting_text, F.text, reply_menu.remove_messages
)
async def back_button_text_handler(
    message: types.Message, state: FSMContext, bot_user: BotUser
):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    inline_menu = await InlineMenu.get(id=state_data["inline_menu_id"])
    inline_menu.back_button_text = message.text  # type: ignore

    dialog_messages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        inline_menu,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(inline_menu),
        text=inline_menu.text,
    )

    await inline_menu.save()
    await state.set_state(AdminReplyMenuState.waiting_action)
    await state.update_data(dialog_messages=dialog_messages)


@router.callback_query(
    AdminReplyMenuState.waiting_action,
    markups.AdminInlineMenuCallbackData.filter(
        F.type == markups.AdminInlineMenuCallbackData.Type.edit_name
    ),
    reply_menu.remove_messages,
)
async def edit_name_handler(
    query: types.CallbackQuery, state: FSMContext, bot_user: BotUser
):
    data = markups.AdminInlineMenuCallbackData.unpack(query.data)  # type: ignore
    enter_name_message = await bot.send_message(
        bot_user.id, bot.phrases.admin.enter_name
    )
    await state.set_state(EditNameState.waiting_name)
    await state.update_data(
        dialog_messages=[enter_name_message], inline_menu_id=data.menu_id
    )


@router.message(EditNameState.waiting_name, F.text, reply_menu.remove_messages)
async def name_handler(message: types.Message, state: FSMContext, bot_user: BotUser):
    state_data = await state.get_data()
    menu: ReplyMenu = state_data["menu"]
    inline_menu = await InlineMenu.get(id=state_data["inline_menu_id"])
    inline_menu.name = message.text  # type: ignore

    dialog_mesages = await reply_menu.send_reply_menu(
        bot_user,
        menu,
        inline_menu,
        reply_markup=await markups.create_admin_reply_menu_markup(menu),
        inline_markup=await markups.create_admin_inline_menu_markup(inline_menu),
    )

    await inline_menu.save()
    await state.set_state(AdminReplyMenuState.waiting_action)
    await state.update_data(dialog_messages=dialog_mesages)
