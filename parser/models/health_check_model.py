from pydantic import Field
from pydantic import BaseModel
from .parser_state_model import ParserStateModel


class HealthCheckModel(BaseModel):
    status: str = Field(example="ok")
    parsers: dict[str, ParserStateModel] = Field(example="https://docs.python.org/3/library/typing.html")

    def __repr__(self) -> str:
        return str(self.__dict__)
