from pydantic import BaseModel


class StartFailedModel(BaseModel):
    status: bool = False
    message: str = "Данные по выбранному URL недоступны"
