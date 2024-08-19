from typing import Generator, Any

import pytest


from app.db import Database
from app.model import Person
from app.repository import PersonRepository
from gfmodules_python_shared.session.db_session import DbSession
from gfmodules_python_shared.session.session_factory import DbSessionFactory


@pytest.fixture()
def session() -> Generator[DbSession, Any, None]:
    db = Database("sqlite:///:memory:")
    db.generate_tables()
    session_factory = DbSessionFactory(db.engine)
    session = session_factory.create()

    yield session


@pytest.fixture()
def repository(session: DbSession) -> PersonRepository:
    return PersonRepository(session)


@pytest.fixture()
def mock_person() -> Person:
    return Person(name="some name")
