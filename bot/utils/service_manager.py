import asyncio
from typing import List

from ..protocols.service import Service


class ServiceManager:
    def __init__(self):
        self._services: List[Service] = []

    def register(self, service: Service):
        self._services.append(service)
        return service

    def unregister(self, service: Service):
        self._services.remove(service)

    async def setup_all(self):
        if not self._services:
            return

        service_setup_coros = (service.setup() for service in self._services)
        await asyncio.gather(*(service_setup_coros))

    async def dispose_all(self):
        if not self._services:
            return

        service_dispose_coros = (service.dispose() for service in self._services)
        await asyncio.gather(*service_dispose_coros)
