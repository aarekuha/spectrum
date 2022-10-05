from pydantic import BaseModel


class StartSuccessModel(BaseModel):
    status: bool = True
    message: str = "Процесс сбора информации запущен"
