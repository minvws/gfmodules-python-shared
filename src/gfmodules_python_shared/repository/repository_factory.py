from typing import Type

from src.gfmodules_python_shared.session.db_session import DbSession
from src.gfmodules_python_shared.repository.repository_base import RepositoryBase, TRepositoryBase


class RepositoryFactory:

    @staticmethod
    def create(
        repo_class: Type[TRepositoryBase], session: DbSession
    ) -> TRepositoryBase:
        if issubclass(repo_class, RepositoryBase):
            return repo_class(session)

        raise ValueError(
            f"repository {repo_class.__name__} is not valid for repository creation"
        )
