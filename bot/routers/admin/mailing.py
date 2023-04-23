from aiogram import F, types
from aiogram3_form import Form, FormField
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from ...bot import bot
from ...services.database.models import BotUser
from . import router


class MailingForm(Form, router=router):
    message: types.Message = FormField(
        enter_message_text=bot.phrases.admin.enter_mailing_message_text,
        filter=F.func(lambda m: m),
    )


@MailingForm.submit()
async def mailing_form_submit_handler(form: MailingForm):
    await form.answer(bot.phrases.admin.mailing_started_message_text)

    all_bot_users = await BotUser.all()
    sent_messages_count = 0

    for bot_user in all_bot_users:
        try:
            await form.message.copy_to(bot_user.id)
        except Exception:
            continue

        sent_messages_count += 1

    await form.answer(
        bot.phrases.admin.sent_messages_message_text_fmt.format(
            sent_messages_count=sent_messages_count
        )
    )


@router.message(Command("mail"))
async def mail_command_handler(_, state: FSMContext):
    await MailingForm.start(state)
