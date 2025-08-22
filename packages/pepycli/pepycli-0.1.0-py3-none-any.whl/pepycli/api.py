from aiohttp import ClientSession
from .config import config

class PepyCliAPI:
    def __init__(self):
        self.headers = {"X-API-Key": config["API_KEY"]}
        self.base_url = "https://api.pepy.tech/api/v2/projects"

    async def _get(self, url: str):
        async with ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status != 200:
                    text = await response.text()
                    raise Exception(f"Error {response.status}: {text}")
                    
                return await response.json()

    async def get_analytics(self, project: str):
        return await self._get(f"{self.base_url}/{project}")

    async def get_project_downloads(self, project: str):
        return await self._get(f"{self.base_url}/{project}/downloads")
