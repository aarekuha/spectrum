import logging
import asyncio
import aiohttp
from asyncio import Queue
from http import HTTPStatus
from typing import Coroutine
from contextlib import suppress
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from bs4.element import ResultSet
from aiohttp import ClientResponse
from aiohttp import ClientSession
from aiohttp import InvalidURL
from aiohttp import ClientConnectorError
from aiohttp import TooManyRedirects
from aiohttp import ServerTimeoutError
from aiohttp import ServerDisconnectedError

from models import SiteModel

class Parser():
    """ Рекурсивная обработка данных сайта """
    _url_site: str
    _url_start: str
    _status_store: dict
    _max_depth: int
    _max_concurrent: int
    _default_timeout_sec: int
    _processed_urls: set[str]
    _client: aiohttp.ClientSession
    _session_timeout: aiohttp.ClientTimeout
    _semaphores: dict[int, asyncio.Semaphore]
    _queue: Queue

    def __init__(
        self,
        queue: Queue,
        start_url: str,
        status_store: dict,
        max_depth: int = 0,
        max_concurrent: int = 1,
        default_timeout_sec: int = 10
    ) -> None:
        """
            start_url: адрес начала обхода ссылок
            max_depth: максимальная глубина обработки ссылок
            max_concurrent: максимальное количество одновременных запросов для каждого уровня
            default_timeout_sec: таймаут ответа (задержавшиеся ответы не обрабатываются)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._queue = queue
        self._url_start = start_url
        self._url_site = "://".join(urlparse(start_url)[:2])
        self._url_domain = urlparse(start_url)[1]
        self._status_store = status_store
        self._max_depth = max_depth
        self._max_concurrent = max_concurrent
        self._default_timeout_sec = default_timeout_sec
        self._semaphores = {level: asyncio.Semaphore(max_concurrent) for level in range(max_depth + 1)}
        self._processed_urls = set()
        self._session_timeout = aiohttp.ClientTimeout(
            total=None,
            sock_connect=default_timeout_sec,
            sock_read=default_timeout_sec
        )

    def _get_links(self, url: str, html: str) -> set:
        """ Сбор ссылок из документа """
        result_set: set = set()
        soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
        all_links: ResultSet = soup.find_all('a')
        for next_link in all_links:
            link: str = next_link.get('href')
            if link:
                # Обработка относительных ссылок
                if link.startswith('/'):
                    link = f"{self._url_site}{link}"
                result_set.add(link)

        self._queue.put_nowait(SiteModel.from_soup(url=url, soup=soup))

        return result_set

    async def _fetch(self, session: ClientSession, url: str, current_depth: int) -> None:
        """ Рекурсивная процедура обработки каждого адреса """
        if current_depth > self._max_depth:
            return

        # Подавление "не интересных" исключений
        with suppress(
            InvalidURL,
            ClientConnectorError,
            AssertionError,
            TooManyRedirects,
            ServerTimeoutError,
            UnicodeError,
            ServerDisconnectedError,
        ):
            # ! Семафор для каждой глубины, запрос данных
            async with self._semaphores[current_depth], session.get(url=url) as response:
                self._processed_urls.add(url)
                if response.status == HTTPStatus.OK:
                    # Подавление в случае ошибки с кодировкой
                    with suppress(UnicodeDecodeError):
                        html: str = await response.text()
                        links: set = self._get_links(url=url, html=html)
                        # Добавить в обработку только новые URL'ы
                        links_to_fetch = links - self._processed_urls
                        # Формирование задач на обработку "в глубину"
                        tasks: list[Coroutine] = []
                        for url in links_to_fetch:
                            tasks.append(
                                self._fetch(
                                    session=session,
                                    url=url,
                                    current_depth=current_depth + 1
                                )
                            )
                        await asyncio.gather(*tasks)

    async def check_site_avail(self, session) -> bool:
        """ Первичная проверка доступности ресурса """
        async with session.get(self._url_start, allow_redirects=True) as response:
            return response.status == HTTPStatus.OK

    async def _process(self) -> None:
        """ Процесс сбора данных """
        if len(self._url_domain) > 64:
            raise Exception("Domain name too long")
        async with aiohttp.ClientSession(timeout=self._session_timeout) as session:
            await asyncio.create_task(self._fetch(session=session, url=self._url_start, current_depth=0))
        self._remove_from_store()

    async def start(self) -> bool:
        """
            Запуск фонового процесса сбора данных
            Возвращает:
                - True, если запуск был осуществлен
                - False, если недоступен стартовый URL
        """
        # Предварительная проверка доступности стартового URL
        async with aiohttp.ClientSession(timeout=self._session_timeout) as session:
            if not await self.check_site_avail(session):
                return False
        self.logger.info(f"Started: {self._url_start}...")
        # Запуск фонового процесса обработки
        self._task = asyncio.create_task(self._process())
        # Уведомление об успехе старта
        return True

    def _remove_from_store(self, message: str = "Completed") -> None:
        """ Удаление состояния и ссылок на task """
        # После завершения работы ссылок не остаётся, экземпляр Parser'а будет удалён GC
        del self._status_store[self._url_start]
        self.logger.info(f"{message}: {self._url_start}...")

    def cancel(self) -> None:
        self._task.cancel()
        self._remove_from_store(message="Cancelled")

    @property
    def __dict__(self):
        """ Поле для формирования описания Парсера в OpenAPI """
        return {
            "status": "Processing...",
            "max_depth": self._max_depth,
            "max_concurrent": self._max_concurrent,
            "default_timeout_sec": self._default_timeout_sec,
        }
