from .request import Base

from aiohttp import ClientSession
from typing import Dict, Any

BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterAPI(Base):
    ENDPOINTS = {
        "completion": "/completions",
        "chat_completion": "/chat/completions",
        "generation": "/generation",
        "models": "/models",
        "credits": "/credits"
    }

    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        super().__init__(base_url=base_url)

    async def send_completion(self, prompt: str) -> Dict[str, Any]:
        data = {"model": self.model, "message": [{"role": "user", "content": prompt}]}
        return await self._post(self.ENDPOINTS["completion"], data)

    async def chat_completion(self, prompt: str, messages: list = None) -> Dict[str, Any]:
        if messages is None:
            messages = []
            
        messages.append({"role": "user", "content": prompt})
        data = {"model": self.model, "messages": messages}
        return await self._post(self.ENDPOINTS["chat_completion"], data)

    async def get_generation(self, generation_id: str) -> Dict[str, Any]:
        return await self._get(f"{self.ENDPOINTS['generation']}/{generation_id}")

    async def get_list_of_models(self) -> Dict[str, Any]:
        return await self._get(self.ENDPOINTS["models"])

    async def get_credits(self) -> Dict[str, Any]:
        return await self._get(self.ENDPOINTS["credits"])
