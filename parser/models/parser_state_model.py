from pydantic import Field
from pydantic import BaseModel

from modules import Parser


class ParserStateModel(BaseModel):
    max_depth: int = Field(example=2)
    max_concurrent: int = Field(example=10)
    default_timeout_sec: int = Field(example=10)
    task: Parser = Field(example="<html><body></body></html>")

    class Config:
        arbitrary_types_allowed = True
