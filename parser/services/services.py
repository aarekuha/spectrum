from asyncio import Queue

from modules import Config
from .parser_service import ParserService
from .database import Database


class Services:
    """ Оркестратор сервисов """
    parser_service: ParserService
    queue: Queue
    database: Database

    def __init__(self, config: Config) -> None:
        self.queue = Queue()
        self.parser_service = ParserService(queue=self.queue)
        self.database = Database(
            host=config.DB_HOSTNAME,
            port=int(config.DB_PORT),
            database=config.DB_DATABASE,
            username=config.DB_USERNAME,
            password=config.DB_PASSWORD,
            queue=self.queue,
        )
