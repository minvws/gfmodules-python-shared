from typing import TypeVar, Type

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T")


class EntryNotFound(NoResultFound):
    def __init__(self, model: Type[T]) -> None:
        if issubclass(model, DeclarativeBase):
            super().__init__(f"No result found in {model.__name__}")
        else:
            raise TypeError(
                f"Type {model} not a subclass of SQLAlchemy DeclarativeBase"
            )
