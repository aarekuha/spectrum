from asyncio import Queue

from .service_base import ServiceBase
from modules import Parser

class ParserService(ServiceBase):
    _queue: Queue
    _status_store: dict[str, Parser]
    _limit_concurrent_processes: int

    def __init__(self, queue: Queue, limit_concurrent_processes: int):
        super().__init__()
        self._status_store = {}
        self._queue = queue
        self._limit_concurrent_processes = limit_concurrent_processes

    def is_url_processing(self, start_url: str) -> bool:
        """ Поиск запущенного процесса сбора данных по URL """
        return start_url in self._status_store

    def cancel_by_url(self, start_url: str) -> None:
        """ Останов задачи по стартовому URL """
        self._status_store[start_url].cancel()

    def is_busy(self) -> bool:
        return len(self._status_store) > self._limit_concurrent_processes

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
        if start_url in self._status_store:
            return False
        # Подготовка Парсера
        parser: Parser = Parser(
            queue=self._queue,
            start_url=start_url,
            status_store=self._status_store,
            max_depth=max_depth,
            max_concurrent=max_concurrent,
            default_timeout_sec=default_timeout_sec,
        )
        # Обогащение состояния задач деталями
        self._status_store[start_url] = parser
        return await parser.start()
