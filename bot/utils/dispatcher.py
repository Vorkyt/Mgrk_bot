from typing import Any

from aiogram import Dispatcher as AiogramDispatcher

from .service_manager import ServiceManager


class Dispatcher(AiogramDispatcher):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.services = ServiceManager()
