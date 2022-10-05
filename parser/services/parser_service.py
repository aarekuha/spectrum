from asyncio import Queue

from .service_base import ServiceBase
from modules import Parser

class ParserService(ServiceBase):
    _parsers: dict
    _queue: Queue

    def __init__(self, queue: Queue):
        super().__init__()
        self._parsers = {}
        self._queue = queue

    async def parse_site(
        self,
        start_url: str,
        max_depth: int,
        max_concurrent: int,
        default_timeout_sec: int
    ) -> bool:
        """
            Запуск процедуры обхода сайта
            start_url: адрес начала обхода ссылок
            max_depth: максимальная глубина обработки ссылок
            max_concurrent: максимальное количество одновременных запросов для каждого уровня
            default_timeout_sec: таймаут ответа (задержавшиеся ответы не обрабатываются)
        """
        if start_url in self._parsers:
            return False
        # Подготовка Парсера
        parser: Parser = Parser(
            queue=self._queue,
            start_url=start_url,
            max_depth=max_depth,
            max_concurrent=max_concurrent,
            default_timeout_sec=default_timeout_sec,
        )
        # Обогащение health_check'а сервиса деталями о состоянии
        self._parsers.update({
            start_url: {
                "max_depth": max_depth,
                "max_concurrent": max_concurrent,
                "default_timeout_sec": default_timeout_sec,
            },
        })
        return await parser.start(status_store=self._parsers)
