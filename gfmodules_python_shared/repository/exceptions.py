from typing import Type

from sqlalchemy.exc import NoResultFound

from gfmodules_python_shared.schema.sql_model import SQLModelBase


class EntryNotFound(NoResultFound):
    def __init__(self, model: Type[SQLModelBase]) -> None:
        super().__init__(f"No result found in {model.__name__}")
