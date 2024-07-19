from typing import Type

from sqlalchemy.orm import DeclarativeBase

from src.gfmodules_python_shared.repository.repository_base import GenericRepository
from src.gfmodules_python_shared.session.db_session import DbSession


class RepositoryFactory:

    @staticmethod
    def create(
        repo_class: Type[GenericRepository[DeclarativeBase]], session: DbSession
    ) -> GenericRepository[DeclarativeBase]:
        return repo_class(session)
