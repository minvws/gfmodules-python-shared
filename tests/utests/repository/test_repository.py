from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Any, TypeAlias
from uuid import UUID

import pytest
from sqlalchemy import ColumnExpressionArgument
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session, sessionmaker

from app.model import Person
from app.repository import PersonRepository
from gfmodules_python_shared.repository.exceptions import EntryNotFound
from gfmodules_python_shared.schema.sql_model import TSQLModel
from tests.utests.utils import are_the_same_entity

Inserter: TypeAlias = Callable[[Session, Iterable[TSQLModel]], None]


@pytest.fixture(scope="module")
def people(
    session_maker: sessionmaker[Session],
    insert_entities: Inserter[Person],
) -> dict[str, Person]:
    johns = {
        "snow": Person(
            id=UUID("caad98ff-53f6-4451-9d74-1520f7c5dbe5"),
            name="John Snow",
            age=77,
            created_at=datetime.fromisoformat("2021-09-19 14:02"),
        ),
        "hill": Person(
            id=UUID("1a2c7291-d76c-4230-b30f-5bb38d3d2f61"),
            name="John Hill",
            age=35,
            created_at=datetime.fromisoformat("2023-09-19 14:02"),
        ),
        "stone": Person(
            id=UUID("54db31bc-44e8-4330-993f-8d49006cb7c1"),
            name="John Stone",
            age=72,
            created_at=datetime.fromisoformat("2020-09-19 14:02"),
        ),
        "storm": Person(
            id=UUID("bb98caa7-e4a9-4b67-9ac3-6cf8988272bf"),
            name="John Storm",
            age=75,
            created_at=datetime.fromisoformat("2024-09-19 14:02"),
        ),
        "rivers": Person(
            id=UUID("4447813d-2040-4124-ae51-f9732ce31334"),
            name="John Rivers",
            age=5,
            created_at=datetime.fromisoformat("2014-09-19 14:02"),
        ),
        "waters": Person(
            id=UUID("042c2b10-1192-4c99-a025-67131bdbfbb5"),
            name="John Waters",
            age=95,
            created_at=datetime.fromisoformat("2002-05-19 14:02"),
        ),
        "pyke": Person(
            id=UUID("6c556a4a-dd47-40ba-8e92-d6761d803f62"),
            name="John Pyke",
            age=55,
            created_at=datetime.fromisoformat("2004-09-19 14:02"),
        ),
        "sand": Person(
            id=UUID("4869daa2-c226-4ab8-950f-605e2342e32c"),
            name="John Sand",
            age=74,
            created_at=datetime.fromisoformat("2016-09-19 14:02"),
        ),
    }
    with session_maker() as session:
        insert_entities(session, johns.values())
        # for john in johns.values():
        #     session.refresh(john)
        return johns


# NOTE: tests READ only operations on empty database Tests
#
def test_count_should_return_0_given_no_entity_in_db(session: Session) -> None:
    assert not PersonRepository(session).count()


def test_get_should_return_none_when_value_is_not_found(session: Session) -> None:
    assert PersonRepository(session).get(name="non-matching value") is None


def test_get_many_should_return_empty_list_when_filter_value_does_not_match(
    session: Session,
) -> None:
    assert not PersonRepository(session).get_many(name="doesn't exists")


def test_get_should_raise_invalid_request_error_when_given_a_bad_property(
    session: Session,
) -> None:
    with pytest.raises(
        InvalidRequestError, match="wrong_property is not a column in the Person"
    ):
        PersonRepository(session).get(wrong_property="some value")


def test_get_or_fail_should_raise_entry_not_found_when_given_a_bad_value(
    session: Session,
) -> None:
    with pytest.raises(EntryNotFound, match="No result found in Person"):
        PersonRepository(session).get_or_fail(name="bad value")


def test_get_by_priority_should_raise_attribute_error_given_bad_attribute(
    session: Session,
) -> None:
    with pytest.raises(AttributeError, match="bad key is not a column in the Person"):
        PersonRepository(session).get_by_property("bad key", ["doesn't matter"])


# NOTE: tests READ only operations on populated database
#
def test_count_should_return_n_total_given_n_entity_in_db(
    session: Session, people: dict[str, Person]
) -> None:
    assert PersonRepository(session).count() == len(people)


@pytest.mark.parametrize("method", ("get", "get_or_fail"))
def test_get_x_should_return_an_entity_given_proper_attribute_and_value(
    session: Session, people: dict[str, Person], method: str
) -> None:
    repository = PersonRepository(session)
    assert all(
        (actual_person := getattr(repository, method)(id=person.id))
        and are_the_same_entity(actual_person, person)
        for person in people.values()
    )


@pytest.mark.parametrize(
    "args, house_names",
    (
        pytest.param(
            ("name", ["snow", "storm"]),
            ("snow", "storm"),
            id="should return multiple entities given multiple values",
        ),
        pytest.param(
            ("name", ["John"]),
            ("snow", "storm", "stone", "pyke", "hill", "sand", "rivers", "waters"),
            id="should return multiple entities given single value",
        ),
        pytest.param(
            ("name", ["snow", "wrong value"]),
            ("snow",),
            id="should return single entity, given multiple values",
        ),
        pytest.param(
            ("name", ["wrong value"]),
            (),
            id="should return empty list given wrong value",
        ),
    ),
)
def test_get_by_priority(
    session: Session,
    people: dict[str, Person],
    args: tuple[str, list[str]],
    house_names: tuple[str, ...],  # illegitimate
) -> None:
    actual = PersonRepository(session).get_by_property(*args)
    expected = (
        person for person in people.values() if person.name.split()[-1] in house_names
    )

    assert isinstance(actual, list) and all(
        are_the_same_entity(a, e) for a, e in zip(actual, expected)
    )


@pytest.mark.parametrize(
    "kargs, house_names",
    (
        pytest.param(
            {},
            ("waters", "pyke", "rivers", "sand", "stone", "snow", "hill", "storm"),
            id="should return all entities ordered by created date given no kwargs",
        ),
        pytest.param(
            {"limit": 2},
            ("waters", "pyke"),
            id="should return top two entities ordered by name given limit=2",
        ),
        pytest.param(
            {"offset": 3},
            ("sand", "stone", "snow", "hill", "storm"),
            id="should skip the first three entities"
            " and return the rest ordered by created date"
            " given offset=3",
        ),
        pytest.param(
            {"order_by": (Person.age,)},
            ("waters", "pyke", "rivers", "sand", "stone", "snow", "hill", "storm"),
            id="should return all entities ordered by created date and age"
            " given order_by=(Person.age,)",
        ),
        pytest.param(
            {"limit": 2, "offset": 3},
            ("sand", "stone"),
            id="should skip the first two entities and"
            " return the next three ordered by name"
            " given limit=2 and offset=3",
        ),
        pytest.param(
            {"limit": 2, "order_by": (Person.age.asc(),)},
            ("waters", "pyke"),
            id="should order entities by created date and age ascending"
            " and return top two entities"
            " given limit=2 and order_by=(Person.age,)",
        ),
        pytest.param(
            {"offset": 3, "order_by": (Person.age.desc(),)},
            ("sand", "stone", "snow", "hill", "storm"),
            id="should order entities by created date and age descending,"
            " skip the first three entities and return the rest"
            " given offset=3 and order_by=(Person.age.desc(),)",
        ),
        pytest.param(
            {"limit": 2, "offset": 3, "order_by": (Person.age,)},
            ("sand", "stone"),
            id="should order entities by created date and age,"
            " skip the first three entities and return the next two"
            " given limit=2, offset=3, and order_by=(Person.age,)",
        ),
    ),
)
def test_get_many(
    session: Session,
    people: dict[str, Person],
    kargs: dict[str, int | tuple[ColumnExpressionArgument[Any], ...]],
    house_names: tuple[str, ...],  # illegitimate
) -> None:
    expected = (
        person for person in people.values() if person.name.split()[-1] in house_names
    )
    assert all(
        are_the_same_entity(actual, entity)
        for actual, entity in zip(PersonRepository(session).get_many(**kargs), expected)  # type: ignore
    )


@pytest.mark.parametrize(
    "args, house_names",
    (
        pytest.param(
            ("name", ["John Snow", "John Waters"]),
            ("snow", "waters"),
            id="should return multiple entities given multiple values",
        ),
        pytest.param(
            ("name", ["John Sand"]),
            ("sand",),
            id="should return single entity given single value",
        ),
    ),
)
def test_get_by_priority_exact(
    session: Session,
    people: dict[str, Person],
    args: tuple[str, list[str]],
    house_names: tuple[str, ...],  # illegitimate
) -> None:
    actual = PersonRepository(session).get_by_property_exact(*args)
    expected = (
        person for person in people.values() if person.name.split()[-1] in house_names
    )
    assert isinstance(actual, list) and all(
        are_the_same_entity(a, e) for a, e in zip(actual, expected)
    )


@pytest.mark.parametrize(
    "args",
    (
        pytest.param(
            ("name", ["John Snow", "John Waters", "no match"]),
            id="given majority match",
        ),
        pytest.param(
            ("name", ["John Sand", "no match"]),
            id="single match",
        ),
        pytest.param(
            ("name", ["no match"]),
            id="no match",
        ),
    ),
)
def test_get_by_priority_exact_should_raise_entry(
    args: tuple[str, list[str]], session: Session, people: dict[str, Person]
) -> None:
    with pytest.raises(EntryNotFound, match="No result found in Person"):
        PersonRepository(session).get_by_property_exact(*args)


# NOTE: tests WRITE operations on empty database
#
def test_delete_should_raise_invalad_request_error_given_a_non_existing_entity(
    session: Session,
) -> None:
    with pytest.raises(InvalidRequestError):
        PersonRepository(session).delete(
            Person(id="a9c4e465-a01f-4d78-952f-d42c4b03ced7", name="doesn't exists")
        )


def test_create_should_add_entity_to_db_given_new_entity(session: Session) -> None:
    repository = PersonRepository(session)
    repository.create(person := Person(name="John Dow"))
    assert are_the_same_entity(repository.get_or_fail(name=person.name), person)


# NOTE: tests WRITE operations on populated database
#
def test_delete_should_delete_entity_given_it_exists_in_db(
    session: Session,
    people: dict[str, Person],
) -> None:
    repository = PersonRepository(session)
    with session.begin():
        snow = repository.get_or_fail(id=people["snow"].id)
        repository.delete(snow)
    assert snow.id is not None
    assert repository.get(id=snow.id) is None
