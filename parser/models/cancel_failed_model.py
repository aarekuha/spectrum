from pydantic import BaseModel


class CancelFailedModel(BaseModel):
    status: bool = False
    message: str = "Процесс с указанным стартовым URL не найден"
