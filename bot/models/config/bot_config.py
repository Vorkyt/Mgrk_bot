from pydantic import Field

from ..config_model import ConfigModel


class BotConfig(ConfigModel):
    __filenames__ = ("_config_dev.json", "config.json")

    bot_token: str = Field("API токен из @BotFather")
    admin_user_ids: list[int] = Field([])
    database_uri: str = Field("sqlite://database.sqlite3")
