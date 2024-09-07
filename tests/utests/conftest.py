from collections.abc import Callable, Iterator
from typing import Type
from uuid import UUID

import inject
import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.container import container_config
from app.model import Person
from gfmodules_python_shared.io.container import setup_container
from gfmodules_python_shared.repository import T
from gfmodules_python_shared.repository.base import GenericRepository


@pytest.fixture(scope="module", autouse=True)
def with_container() -> None:
    setup_container(container_config)


@pytest.fixture(scope="module")
def session_maker() -> sessionmaker[Session]:
    return inject.instance(sessionmaker[Session])


@pytest.fixture
def session(session_maker: sessionmaker[Session]) -> Iterator[Session]:
    with session_maker() as session:
        yield session


@pytest.fixture(scope="module")
def person() -> Person:
    return Person(id=UUID("caad98ff-53f6-4451-9d74-1520f7c5dbe5"), name="some person")


@pytest.fixture(scope="module")
def insert_entity() -> (
    Callable[[Session, Type[GenericRepository[T]], T], GenericRepository[T]]
):
    def inserter(
        session: Session,
        repository_type: Type[GenericRepository[T]],
        entity: T,
    ) -> GenericRepository[T]:
        repository = repository_type(session)
        with session.begin():
            if repository.get(id=entity.id) is None:  # type: ignore
                repository.create(entity)
        return repository

    return inserter
