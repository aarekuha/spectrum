from typing import cast
from sqlalchemy import select
from sqlalchemy.sql.selectable import Select
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from schemas import Site


class Database():
    _engine: AsyncEngine

    def __init__(self,
        host: str,
        port: int | None,
        database: str,
        username: str,
        password: str,
    ) -> None:
        _host: str = host + (f":{port}" if port else '')
        _dsn = f"postgresql+asyncpg://{username}:{password}@{_host}/{database}"
        self._engine = create_async_engine(_dsn, echo=True)

    async def get_site_html(self, url: str) -> str:
        async with self._engine.connect() as connection:
            query: Select = select(Site).where(Site.url == url)
            result: CursorResult = await connection.execute(query)
            finded_site: Row | None = result.fetchone()
            if not finded_site:
                return ""
            site: Site = cast(Site, finded_site)

        return str(site.html)

    async def get_urls_list(self, limit: int) -> list[str]:
        async with self._engine.connect() as connection:
            query: Select = select(Site).limit(limit)
            result: CursorResult = await connection.execute(query)
            urls_list: list[str] = []
            for site in result:
                urls_list.append(site.url)

        return urls_list
