from pydantic import Field
from pydantic import BaseModel


class ListElementModel(BaseModel):
    url: str = Field(example="https://habr.com/ru/post/420129/")
    title: str = Field(example="Паттерны корутин asyncio: за пределами await / Хабр")
