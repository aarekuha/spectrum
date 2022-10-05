from __future__ import annotations

from bs4 import BeautifulSoup
from pydantic import Field
from pydantic import BaseModel


class SiteModel(BaseModel):
    html: str = Field(example="<html><body></body></html>")
    url: str = Field(example="https://docs.python.org/3/library/typing.html")
    title: str = Field(example="typing — Support for type hints")

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_soup(url: str, soup: BeautifulSoup) -> SiteModel:
        html: str = str(soup)
        title: str = soup.title.text if soup.title else ""
        return SiteModel(html=html, url=url, title=title)
