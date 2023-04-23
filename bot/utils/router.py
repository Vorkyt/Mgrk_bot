from aiogram.dispatcher.router import Router as AiogramRouter
from aiogram.filters import BaseFilter


class Router(AiogramRouter):
    def bind_filter(self, bound_filter: BaseFilter) -> None:
        for observer in self.observers.values():
            observer.filter(bound_filter)
