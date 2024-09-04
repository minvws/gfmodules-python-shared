from typing import Type

from sqlalchemy.orm import DeclarativeBase, Session

from gfmodules_python_shared.repository.base import GenericRepository


class RepositoryFactory:

    @staticmethod
    def create(
        repo_class: Type[GenericRepository[DeclarativeBase]], session: Session
    ) -> GenericRepository[DeclarativeBase]:
        return repo_class(session)
