from tortoise import Tortoise

from ...bot import bot


class DatabaseService:
    async def setup(self):
        await Tortoise.init(
            modules={"models": ["bot.services.database.models"]},
            db_url=bot.config.database_uri,
        )

        await Tortoise.generate_schemas()

    async def dispose(self):
        await Tortoise.close_connections()
