import logging

from . import middleware, routers, services
from .bot import bot, dispatcher
from .utils.paths import root_path, routers_path


@dispatcher.startup()
async def on_startup():
    await services.setup(dispatcher)
    me = await bot.get_me()
    print(bot.phrases.bot_started.format(me=me))


@dispatcher.shutdown()
async def on_shutdown():
    await services.dispose(dispatcher)


def import_routers():
    for router_dir_path in routers_path.glob("*"):
        if not router_dir_path.is_dir() or (
            router_dir_path.stem.startswith("__")
            and router_dir_path.stem.endswith("__")
        ):
            continue

        sorted_handler_file_paths = sorted(
            router_dir_path.glob("*.*"), key=lambda p: p.stem
        )

        for handler_file_path in sorted_handler_file_paths:
            if not handler_file_path.is_file():
                continue

            __import__(f"bot.routers.{router_dir_path.stem}.{handler_file_path.stem}")


def main():
    log_filename = str((root_path / "logs.log").resolve())

    logging.basicConfig(
        filename=log_filename,
        level=logging.ERROR,
        format=r"%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s",
    )

    middleware.setup(dispatcher)
    import_routers()
    dispatcher.include_router(routers.root_handlers_router)

    used_update_types = dispatcher.resolve_used_update_types()
    dispatcher.run_polling(bot, allowed_updates=used_update_types)


main()
