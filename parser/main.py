import logging
import uvicorn
import asyncio
from typing import Dict
from fastapi import status
from fastapi import FastAPI
from fastapi import Depends
from fastapi import Query
from fastapi import HTTPException
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from fastapi.responses import JSONResponse

from models import StartSuccessModel
from models import StartLimitedModel
from models import StartFailedModel
from models import CancelSuccessModel
from models import CancelFailedModel
from modules import Config
from services import Services


config: Config = Config()
app = FastAPI(
    title=config.APP_TITLE,
    description=config.APP_DESCRIPTION,
    contact={
        "name": "Rekukha Alexander (+7 901 437 77 67)",
        "email": "aarekuha@gmail.com",
    },
)
security = HTTPBasic()
services: Services = Services(config=config)
logger: logging.Logger = logging.getLogger("main.py")


@app.get(path="/",
    responses={
        status.HTTP_200_OK: {"description": "Сервис доступен", "model": Dict[str, str]},
    },
    status_code=status.HTTP_200_OK,
    summary="Состояние сервиса и запущенных процессов",
)
async def health_check():
    return {
        "status": "ok",
        "parsers": services.parser_service._status_store,
    }


def basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """ Базовая авторизация запроса на парсинг """
    is_correct_username: bool = credentials.username == config.AUTH_USERNAME
    is_correct_password: bool = credentials.password == config.AUTH_PASSWORD
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.put(path="/init_parse_in_background",
    responses={
        status.HTTP_200_CREATED: {
            "description": "Запуск процесса произведен успешно",
            "model": StartSuccessModel,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Указанный URL недоступен",
            "model": StartFailedModel,
        },
        status.HTTP_409_CONFLICT: {
            "description": "Достигнут предел одновременных задач",
            "model": StartLimitedModel,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Переданы неправильные аргументы",
        },
    },
    summary="Запуск процесса фоновой задачей",
    dependencies=[Depends(basic_auth)],
)
async def init_parse_in_background(
    start_url: str = Query(
        description="Стартовый адрес",
        default="https://habr.com/ru/post/420129/",
        max_length=250,  # Ограничение количества знаков
    ),
    max_depth: int = Query(
        description="Максимальная глубина обхода ссылок",
        default=1,
        gt=0,  # Минимальное значение
        lt=5,  # Маскимальное значение
    ),
    max_concurrent: int = Query(
        description="Максимальное количество одновременных запросов",
        default=1,
        gt=0,  # Минимальное значение
        lt=30,  # Маскимальное значение
    ),
    default_timeout_sec: int = Query(
        description="Максимальный таймаут ожидания ответа каждого запроса",
        default=10,
        gt=0.1,  # Минимальное значение
        lt=60,  # Маскимальное значение
    ),
):
    """
        Инициация процесса сбора информации по ссылкам в указанную глубину.
        Сбор производится асинхронно. Состояние запущенных процессов доступно
        [по ссылке /](/)
    """
    if services.parser_service.is_busy():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=StartLimitedModel().dict(),
        )

    if await services.parser_service.parse_site(
        start_url=start_url,
        max_depth=max_depth,
        max_concurrent=max_concurrent,
        default_timeout_sec=default_timeout_sec,
    ):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=StartSuccessModel().dict(),
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=StartFailedModel().dict(),
        )


@app.patch(path="/cancel",
    responses={
        status.HTTP_200_OK: {
            "description": "Задача на сбор остановлена",
            "model": CancelSuccessModel,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Задача с указанным стартовым URL не найдена",
            "model": CancelFailedModel,
        },
    },
    summary="Останов запущенного процесса",
    dependencies=[Depends(basic_auth)],
)
async def cancel_parse_process(
    start_url: str = Query(
        description="Стартовый адрес",
        default="https://habr.com/ru/post/420129/",
        max_length=250,  # Ограничение количества знаков
    ),
) -> JSONResponse:
    """ Останов запущенного процесса путём указания стартового URL """
    if not services.parser_service.is_url_processing(start_url):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=CancelFailedModel().dict()
        )

    services.parser_service.cancel_by_url(start_url=start_url)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=CancelSuccessModel().dict()
    )


@app.on_event("startup")
async def startup():
    asyncio.create_task(services.database.start_listener())


@app.on_event("shutdown")
async def shutdown():
    services.database.close()

if __name__ == '__main__':
    uvicorn.run("main:app",
                host='0.0.0.0',
                port=int(config.APP_PORT),
                log_config=None,
                log_level=config.log_level.lower(),
                access_log=False,
                workers=1)
