from asyncio import Queue

from parser.models import SiteModel
from parser.services.database import Database

DB: list[dict] = []

class MockedDB(Database):
    """ Заглушка базы данных """
    def __init__(self, host: str, port: int | None, database: str, username: str, password: str, queue: Queue) -> None:
        super().__init__(host, port, database, username, password, queue)

    async def _put(self, site: SiteModel) -> None:
        DB.append({
            "url": site.url,
            "html": site.html,
            "title": site.title,
        })
