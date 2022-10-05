from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Site(Base):
    __tablename__ = "sites_info"

    id: Column[int] = Column(Integer, primary_key=True)
    url: Column[str] = Column(String, unique=True, index=True)
    title: Column[str] = Column(String, unique=True)
    html: Column[str] = Column(String)
