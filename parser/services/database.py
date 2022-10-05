import asyncpg
from asyncio import Queue

from models import SiteModel

from .service_base import ServiceBase


class Database(ServiceBase):
    _dsn: str
    _queue: Queue
    _pool: asyncpg.Pool | None = None
    is_listener_started: bool = False

    def __init__(self,
        host: str,
        port: int | None,
        database: str,
        username: str,
        password: str,
        queue: Queue
    ) -> None:
        super().__init__()
        _host: str = host + (f":{port}" if port else '')
        self._dsn = f"postgresql://{username}:{password}@{_host}/{database}"
        self._queue = queue

    async def _put(self, site: SiteModel) -> None:
        if not self._pool:
            self._pool = await asyncpg.create_pool(self._dsn)
            if not self._pool:
                raise Exception("Database connection error...")

        async with self._pool.acquire() as connection:
            await connection.execute(
                "insert into sites_info(url, html, title) values($1, $2, $3) on conflict do nothing",
                site.url, site.html, site.title
            )

    async def start_listener(self) -> None:
        self.is_listener_started = True
        while self.is_listener_started:
            site: SiteModel = await self._queue.get()
            await self._put(site)

    def close(self) -> None:
        self.is_listener_started = False
