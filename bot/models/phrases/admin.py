from pydantic import BaseModel, Field


class AdminPhrases(BaseModel):
    add_button: str = Field("Добавить кнопку")
    remove_button: str = Field("Удалить")
    set_message_in_admin: str = Field("Установите сообщение в админке")
    enter_name: str = Field("Введите название кнопки")
    edit_button_text: str = Field("Изм. текст")
    edit_back_button_text: str = Field('Изм. текст "назад"')
    enter_text: str = Field("Введите текст")
    buttons_horizontal: str = Field("Кнопки строчками")
    buttons_vertical: str = Field("Кнопки столбиком")
    add_url_button: str = Field("Добавить ссылку")
    remove_url_button: str = Field("Удалить ссылку")
    enter_url: str = Field("Введите ссылку")
    edit_file: str = Field("Изменить файл")
    remove_file: str = Field("Удалить файл")
    enter_file: str = Field("Введите файл")
    edit_name: str = Field("Изм. название")
    enter_mailing_message_text: str = Field("Введите сообщение рассылки")
    mailing_started_message_text: str = Field("Рассылка началась")
    sent_messages_message_text_fmt: str = Field("Отправлено {sent_messages_count} сообщений")