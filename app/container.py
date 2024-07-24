import inject

from gfmodules_python_shared.repository import RepositoryFactory
from gfmodules_python_shared.session import DbSessionFactory
from app.db import Database


def container_config(binder: inject.Binder) -> None:
    db = Database(dsn="sqlite:///:memory:")
    binder.bind(Database, db)

    session_factory = DbSessionFactory(db.engine)
    binder.bind(DbSessionFactory, session_factory)

    repository_factory = RepositoryFactory()
    binder.bind(RepositoryFactory, repository_factory)
