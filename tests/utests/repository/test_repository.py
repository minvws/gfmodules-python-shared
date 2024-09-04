from typing import TypeVar
from sqlalchemy.orm import DeclarativeBase, Session
from app.model import Person
from app.repository import PersonRepository

T = TypeVar("T", bound=DeclarativeBase)


def are_the_same_table(actual: T, comparer: T) -> bool:
    return all(
        getattr(actual, key) == getattr(comparer, key)
        for key in actual.__table__.columns.keys()
    )


def test_create(person: Person, session: Session) -> None:
    repository = PersonRepository(session)
    with session.begin():
        repository.create(person)
        actual_person = repository.get(id=person.id)

    assert actual_person and are_the_same_table(actual_person, person)


def test_get(inserted_person: tuple[Session, Person]) -> None:
    session, person = inserted_person
    repository = PersonRepository(session)
    with session.begin():
        actual_person = repository.get(id=person.id)

    assert actual_person and are_the_same_table(actual_person, person)


def test_update(inserted_person: tuple[Session, Person]) -> None:
    session, person = inserted_person
    repository = PersonRepository(session)
    previous_name, person.name = (
        person.name,
        (new_name := "another name"),
    )
    with session.begin():
        repository.update(repository.get_or_fail(id=person.id))

    assert person.name != previous_name
    assert person.name == new_name


def test_delete(inserted_person: tuple[Session, Person]) -> None:
    session, person = inserted_person
    repository = PersonRepository(session)
    with session.begin():
        repository.delete(person)
    assert person.id is not None
    with session.begin():
        assert repository.get(id=person.id) is None
