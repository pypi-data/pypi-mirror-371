from aiohttp import ClientSession
from typing import Dict, Any

class Base:
    def __init__(self, base_url: str):
        self.session: ClientSession | None = None
        self.base_url = base_url

    async def start(self):
        self.session = ClientSession()
        return self

    async def stop(self):
        if self.session:
            await self.session.close()

    async def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        await self.start()

        async with self.session.post(f"{self.base_url}{endpoint}", headers=self.headers, json=data) as response:
            return await response.json()

    async def _get(self, endpoint: str) -> Dict[str, Any]:
        await self.start()

        async with self.session.get(f"{self.base_url}{endpoint}", headers=self.headers) as response:
            return await response.json()
                