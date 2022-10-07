from typing import cast
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.sql.selectable import Select
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from schemas import Site
from models import ListElementModel


class Database():
    """ Сервси для работы с базой данных """
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
        """ Поиск содержимого страницы по её URL """
        async with self._engine.connect() as connection:
            query: Select = select(Site).where(Site.url == url)
            result: CursorResult = await connection.execute(query)
            finded_site: Row | None = result.fetchone()
            if not finded_site:
                return ""
            site: Site = cast(Site, finded_site)

        return str(site.html)

    async def get_urls_list(self, limit: int, url_contains: str, title_contains: str) -> list[ListElementModel]:
        """
            Регистронезависимый поиск списка страниц по URL и/или title страницы
            limit: ограничение величины списка
            url_contains: часть содержимого URL
            title_contains: часть содержимого title
        """
        async with self._engine.connect() as connection:
            query: Select = select(Site)
            if url_contains and len(url_contains.strip()):
                query = query.filter(func.lower(Site.url).contains(url_contains))
            if title_contains and len(title_contains.strip()):
                query = query.filter(func.lower(Site.title).contains(title_contains))
            result: CursorResult = await connection.execute(query.limit(limit))
            urls_list: list[ListElementModel] = []
            for site in result:
                urls_list.append(ListElementModel(url=site.url, title=site.title))

        return urls_list
