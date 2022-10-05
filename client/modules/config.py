import os
import dotenv
import logging


class Config():
    APP_PORT = 8090
    APP_TITLE = "API клинет базы сайтов"
    APP_DESCRIPTION = "Тестовое задание для SpectrumData"

    LOG_FORMAT = "%(asctime)s [%(name)s:%(lineno)s] [%(levelname)s]: %(message)s"

    DB_HOSTNAME = "localhost"
    DB_PORT = 5432
    DB_DATABASE = "spectrum"
    DB_USERNAME = "spectrum"
    DB_PASSWORD = "spectrum"

    DEBUG = 0

    def __init__(self):
        """
            Данные сливаются в конфигурацию (класс) из системного окружения
            * использовать файл .env или docker-environment
        """
        dotenv.load_dotenv()
        self.__dict__.update(os.environ)

        logging.getLogger("uvicorn.access").setLevel(self.log_level)
        logging.basicConfig(level=self.log_level, format=self.LOG_FORMAT)

    @property
    def log_level(self):
        """ Уровень логирования, в зависимости от режима DEBUG """
        return "DEBUG" if self.DEBUG else "INFO"
