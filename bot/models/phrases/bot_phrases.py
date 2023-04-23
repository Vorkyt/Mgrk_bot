from pydantic import Field

from ..config_model import ConfigModel
from .admin import AdminPhrases


class BotPhrases(ConfigModel):
    __filenames__ = ("phrases.json",)

    admin: AdminPhrases = Field(AdminPhrases())  # type: ignore

    bot_started: str = Field("Бот {me.username} успешно запущен")
    back: str = Field("Назад")
    loading_message: str = Field("...")
