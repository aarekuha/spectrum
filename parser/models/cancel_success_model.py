from pydantic import BaseModel


class CancelSuccessModel(BaseModel):
    status: bool = True
    message: str = "Процесс сбора информации остановлен"
