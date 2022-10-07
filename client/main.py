import logging
from fastapi.encoders import jsonable_encoder
import uvicorn
from typing import List
from typing import Dict
from typing import AnyStr
from fastapi import status
from fastapi import FastAPI
from fastapi import Query
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse

from modules import Config
from services import Database
from models import ListElementModel


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


@app.get(path="/ulrs_list",
    responses={
        status.HTTP_200_OK: {
            "description": "Страница найдена",
            "model": List[ListElementModel],
        },
        status.HTTP_404_NOT_FOUND: {"description": "Страница не найдена", "model": AnyStr},
    },
    summary="Запрос списка загруженных URL'ов",
    description="**Регистронезависимый** поиск в базе данных списка загруженных URL'ов"
)
async def get_urls_list(
    limit: int = Query(
        description="Ограничение количества результатов",
        default=100,
        gt=0,
    ),
    url_contains: str = Query(
        description="Регистронезависимый фильтр для поиска по URL",
        default="https://habr.com/ru/post",
        max_length=250,
    ),
    title_contains: str = Query(
        description="Регистронезависимый фильтр для поиска по title страницы",
        default="Паттерны корутин",
        max_length=250,
    ),
):
    """
        **Регистронезависимый** поиск в базе данных списка загруженных URL'ов
        limit: ограничение величины списка
        url_contains: часть содержимого URL
        title_contains: часть содержимого title
    """
    urls_list: list[ListElementModel] = await database.get_urls_list(
        limit=limit,
        url_contains=url_contains,
        title_contains=title_contains,
    )
    if len(urls_list):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(urls_list),
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content="",
        )


if __name__ == '__main__':
    uvicorn.run("main:app",
                host='0.0.0.0',
                port=int(config.APP_PORT),
                log_config=None,
                log_level=config.log_level.lower(),
                access_log=False,
                workers=1)
