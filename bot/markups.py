from enum import IntEnum

from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from .bot import bot
from .services.database.models import InlineMenu, ReplyMenu
from .utils.enums import Alignment


class AdminInlineMenuCallbackData(CallbackData, prefix="admin-inline"):
    class Type(IntEnum):
        child = 0
        add_button = 1
        remove_button = 2
        vertical_alignment = 3
        horizontal_alignment = 4
        add_url_button = 5
        remove_url_button = 6
        edit_file = 7
        remove_file = 8
        edit_text = 9
        edit_back_button_text = 10
        edit_name = 11

    type: Type
    menu_id: int


class UserInlineMenuCallbackData(CallbackData, prefix="user-inline"):
    class Type(IntEnum):
        child = 0

    type: Type
    menu_id: int


async def create_admin_reply_menu_markup(reply_menu: ReplyMenu):
    await reply_menu.fetch_related("parent", "children", "inline_menu")

    builder = ReplyKeyboardBuilder()

    for child in reply_menu.children:
        builder.add(KeyboardButton(text=child.name))

    if reply_menu.alignment == Alignment.vertical:
        builder.adjust(1, repeat=True)
    else:
        builder.adjust(2, repeat=True)

    builder.row(
        KeyboardButton(text=bot.phrases.admin.add_button),
    )

    if len(reply_menu.children) >= 2:
        builder.add(
            KeyboardButton(
                text=bot.phrases.admin.buttons_horizontal
                if reply_menu.alignment == Alignment.vertical
                else bot.phrases.admin.buttons_vertical
            )
        )

    if reply_menu.parent:
        builder.add(KeyboardButton(text=bot.phrases.admin.remove_button))
        builder.row(
            KeyboardButton(text=bot.phrases.admin.edit_name),
            KeyboardButton(text=bot.phrases.admin.edit_back_button_text),
        )
        builder.row(
            KeyboardButton(text=reply_menu.back_button_text or bot.phrases.back),
        )

    return builder.as_markup(resize_keyboard=True)


async def create_admin_inline_menu_markup(inline_menu: InlineMenu):
    await inline_menu.fetch_related("parent", "children", "file")

    builder = InlineKeyboardBuilder()

    for child in inline_menu.children:
        if child.url:
            button = InlineKeyboardButton(text=child.name, url=child.url)
        else:
            button = InlineKeyboardButton(
                text=child.name,
                callback_data=AdminInlineMenuCallbackData(
                    type=AdminInlineMenuCallbackData.Type.child, menu_id=child.id
                ).pack(),
            )

        builder.add(button)

    if inline_menu.alignment == Alignment.vertical:
        builder.adjust(1, repeat=True)
    else:
        builder.adjust(2, repeat=True)

    builder.row(
        InlineKeyboardButton(
            text=bot.phrases.admin.edit_button_text,
            callback_data=AdminInlineMenuCallbackData(
                type=AdminInlineMenuCallbackData.Type.edit_text, menu_id=inline_menu.id
            ).pack(),
        ),
    )

    if inline_menu.parent:
        builder.add(
            InlineKeyboardButton(
                text=bot.phrases.admin.edit_name,
                callback_data=AdminInlineMenuCallbackData(
                    type=AdminInlineMenuCallbackData.Type.edit_name,
                    menu_id=inline_menu.id,
                ).pack(),
            ),
            InlineKeyboardButton(
                text=bot.phrases.admin.edit_back_button_text,
                callback_data=AdminInlineMenuCallbackData(
                    type=AdminInlineMenuCallbackData.Type.edit_back_button_text,
                    menu_id=inline_menu.id,
                ).pack(),
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text=bot.phrases.admin.add_button,
            callback_data=AdminInlineMenuCallbackData(
                type=AdminInlineMenuCallbackData.Type.add_button, menu_id=inline_menu.id
            ).pack(),
        ),
    )

    if len(inline_menu.children) >= 2:
        if inline_menu.alignment == Alignment.vertical:
            button = InlineKeyboardButton(
                text=bot.phrases.admin.buttons_horizontal,
                callback_data=AdminInlineMenuCallbackData(
                    type=AdminInlineMenuCallbackData.Type.horizontal_alignment,
                    menu_id=inline_menu.id,
                ).pack(),
            )
        else:
            button = InlineKeyboardButton(
                text=bot.phrases.admin.buttons_vertical,
                callback_data=AdminInlineMenuCallbackData(
                    type=AdminInlineMenuCallbackData.Type.vertical_alignment,
                    menu_id=inline_menu.id,
                ).pack(),
            )

        builder.add(button)

    builder.row(
        types.InlineKeyboardButton(
            text=bot.phrases.admin.add_url_button,
            callback_data=AdminInlineMenuCallbackData(
                type=AdminInlineMenuCallbackData.Type.add_url_button,
                menu_id=inline_menu.id,
            ).pack(),
        ),
    )

    if any(c.url for c in inline_menu.children):
        builder.add(
            types.InlineKeyboardButton(
                text=bot.phrases.admin.remove_url_button,
                callback_data=AdminInlineMenuCallbackData(
                    type=AdminInlineMenuCallbackData.Type.remove_url_button,
                    menu_id=inline_menu.id,
                ).pack(),
            ),
        )

    builder.row(
        types.InlineKeyboardButton(
            text=bot.phrases.admin.edit_file,
            callback_data=AdminInlineMenuCallbackData(
                type=AdminInlineMenuCallbackData.Type.edit_file, menu_id=inline_menu.id
            ).pack(),
        )
    )

    if inline_menu.file:
        builder.add(
            types.InlineKeyboardButton(
                text=bot.phrases.admin.remove_file,
                callback_data=AdminInlineMenuCallbackData(
                    type=AdminInlineMenuCallbackData.Type.remove_file,
                    menu_id=inline_menu.id,
                ).pack(),
            )
        )

    if inline_menu.parent:
        builder.add(
            InlineKeyboardButton(
                text=bot.phrases.admin.remove_button,
                callback_data=AdminInlineMenuCallbackData(
                    type=AdminInlineMenuCallbackData.Type.remove_button,
                    menu_id=inline_menu.id,
                ).pack(),
            )
        )

        builder.row(
            InlineKeyboardButton(
                text=inline_menu.back_button_text or bot.phrases.back,
                callback_data=AdminInlineMenuCallbackData(
                    type=AdminInlineMenuCallbackData.Type.child,
                    menu_id=inline_menu.parent.id,
                ).pack(),
            )
        )

    return builder.as_markup()


async def create_user_reply_menu_markup(reply_menu: ReplyMenu):
    await reply_menu.fetch_related("parent", "children", "inline_menu")

    builder = ReplyKeyboardBuilder()

    for child in reply_menu.children:
        builder.add(KeyboardButton(text=child.name))

    if reply_menu.alignment == Alignment.vertical:
        builder.adjust(1, repeat=True)
    else:
        builder.adjust(2, repeat=True)

    if reply_menu.parent:
        builder.row(
            KeyboardButton(text=reply_menu.back_button_text or bot.phrases.back),
        )

    return builder.as_markup(resize_keyboard=True)


async def create_user_inline_menu_markup(inline_menu: InlineMenu):
    await inline_menu.fetch_related("parent", "children", "file")

    builder = InlineKeyboardBuilder()

    for child in inline_menu.children:
        if child.url:
            button = InlineKeyboardButton(text=child.name, url=child.url)
        else:
            button = InlineKeyboardButton(
                text=child.name,
                callback_data=UserInlineMenuCallbackData(
                    type=UserInlineMenuCallbackData.Type.child, menu_id=child.id
                ).pack(),
            )

        builder.add(button)

    if inline_menu.alignment == Alignment.vertical:
        builder.adjust(1, repeat=True)
    else:
        builder.adjust(2, repeat=True)

    if inline_menu.parent:
        builder.row(
            InlineKeyboardButton(
                text=inline_menu.back_button_text or bot.phrases.back,
                callback_data=UserInlineMenuCallbackData(
                    type=UserInlineMenuCallbackData.Type.child,
                    menu_id=inline_menu.parent.id,
                ).pack(),
            )
        )

    return builder.as_markup()
