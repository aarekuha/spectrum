import logging
import uvicorn
from typing import List
from typing import Dict
from typing import AnyStr
from fastapi import status
from fastapi import FastAPI
from fastapi import Query
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

from modules import Config
from services import Database


config: Config = Config()
app = FastAPI(
    title=config.APP_TITLE,
    description=config.APP_DESCRIPTION,
    contact={
        "name": "Rekukha Alexander (+7 901 437 77 67)",
        "email": "aarekuha@gmail.com",
    },
)
database: Database = Database(
    host=config.DB_HOSTNAME,
    port=config.DB_PORT,
    database=config.DB_DATABASE,
    username=config.DB_USERNAME,
    password=config.DB_PASSWORD,
)
logger: logging.Logger = logging.getLogger("main.py")


@app.get(path="/",
    responses={
        status.HTTP_200_OK: {"description": "Сервис доступен", "model": Dict[str, str]},
    },
    status_code=status.HTTP_200_OK,
    summary="Состояние сервиса",
)
async def health_check():
    return {"status": "ok"}


@app.get(path="/site", response_class=HTMLResponse,
    responses={
        status.HTTP_200_OK: {"description": "Страница найдена", "model": AnyStr},
        status.HTTP_404_NOT_FOUND: {"description": "Страница не найдена", "model": AnyStr},
    },
    summary="Запрос содержимого страницы",
    description="Поиск в БД собранных данных страницы по её URL"
)
async def get_site_html(
    url: str = Query(
        description="Адрес страницы",
        default="https://habr.com/ru/post/420129/",
    ),
):
    """ Поиск в базе данных содержимого сайта """
    site_html: str = await database.get_site_html(url=url)
    if site_html:
        return HTMLResponse(status_code=200, content=site_html)
    else:
        return HTMLResponse(status_code=404, content="")


@app.get(path="/ulrs_list", response_class=JSONResponse,
    responses={
        status.HTTP_200_OK: {"description": "Страница найдена", "model": List[str]},
        status.HTTP_404_NOT_FOUND: {"description": "Страница не найдена", "model": AnyStr},
    },
    summary="Запрос списка загруженных URL'ов",
    description="Поиск в базе данных списка загруженных URL'ов "
)
async def get_urls_list(
    limit: int = Query(
        description="Ограничение количества результатов",
        default=100,
        gt=0,
    ),
):
    """ Поиск в базе данных списка загруженных URL'ов """
    urls_list: list[str] = await database.get_urls_list(limit=limit)
    if len(urls_list):
        return JSONResponse(status_code=200, content=urls_list)
    else:
        return JSONResponse(status_code=404, content="")


if __name__ == '__main__':
    uvicorn.run("main:app",
                host='0.0.0.0',
                port=int(config.APP_PORT),
                log_config=None,
                log_level=config.log_level.lower(),
                access_log=False,
                workers=1)
