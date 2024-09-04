from typing import Type

from sqlalchemy.orm import Session

from gfmodules_python_shared.repository.base import GenericRepository
from gfmodules_python_shared.repository import T


class RepositoryFactory:

    @staticmethod
    def create(
        repo_class: Type[GenericRepository[T]], session: Session
    ) -> GenericRepository[T]:
        return repo_class(session)
