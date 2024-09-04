from collections.abc import Iterator
from uuid import UUID

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.model import Base, Person
from app.repository import PersonRepository


@pytest.fixture(scope="session")
def engine() -> Engine:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="session")
def session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=True)


@pytest.fixture
def session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    with session_factory() as session:
        yield session


@pytest.fixture(scope="session")
def person() -> Person:
    return Person(id=UUID("2d5e513f-b3d3-4fbd-a83a-5dc5ef06534e"), name="some name")


@pytest.fixture
def inserted_person(
    person: Person, session: Session
) -> Iterator[tuple[Session, Person]]:
    repository = PersonRepository(session)
    with session.begin():
        if repository.get(id=person.id) is None:
            repository.create(person)
    yield session, person
