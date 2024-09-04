from collections.abc import Callable
from typing import Type, TypeAlias
from sqlalchemy.orm import Session
from app.model import Person
from app.repository import PersonRepository
from gfmodules_python_shared.repository import T
from gfmodules_python_shared.repository.base import GenericRepository
from gfmodules_python_shared.repository.repository_factory import RepositoryFactory


Inserter: TypeAlias = Callable[
    [Session, Type[GenericRepository[T]], T], GenericRepository[T]
]


def are_the_same_table(actual: T, comparer: T) -> bool:
    return all(
        getattr(actual, key) == getattr(comparer, key)
        for key in actual.__table__.columns.keys()
    )


def test_create(
    person: Person, repository_factory: RepositoryFactory, session: Session
) -> None:
    repository = repository_factory.create(PersonRepository, session)
    with session.begin():
        repository.create(person)
        actual_person = repository.get(id=person.id)

    assert actual_person and are_the_same_table(actual_person, person)


def test_get(person: Person, session: Session, insert_entity: Inserter[Person]) -> None:
    repository = insert_entity(session, PersonRepository, person)
    with session.begin():
        actual_person = repository.get(id=person.id)

    assert actual_person and are_the_same_table(actual_person, person)


def test_update(
    person: Person, session: Session, insert_entity: Inserter[Person]
) -> None:
    repository = insert_entity(session, PersonRepository, person)
    previous_name, person.name = (
        person.name,
        (new_name := "another name"),
    )
    with session.begin():
        repository.update(repository.get_or_fail(id=person.id))  # type: ignore

    assert person.name != previous_name
    assert person.name == new_name


def test_delete(
    person: Person, session: Session, insert_entity: Inserter[Person]
) -> None:
    repository = insert_entity(session, PersonRepository, person)
    with session.begin():
        repository.delete(person)
    assert person.id is not None
    with session.begin():
        assert repository.get(id=person.id) is None
