from io import BytesIO

from aiogram import types
from aiogram.filters.command import Command
from openpyxl import Workbook

from ...services.database.models import BotUser
from . import router


@router.message(Command("export"))
async def export_command_handler(message: types.Message):
    bot_users = await BotUser.all()

    wb = Workbook()
    ws = wb.active

    title_row = (
        "ID",
        "Full name",
        "Username",
    )

    ws.append(title_row)  # type: ignore

    for bot_user in bot_users:
        ws.append(  # type: ignore
            (
                str(bot_user.id),
                bot_user.full_name,
                f"@{bot_user.username}" if bot_user.username else "",
            )
        )

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    input_file = types.BufferedInputFile(buffer.read(), "users.xlsx")

    await message.answer_document(input_file)
