from collections.abc import Callable, Iterator
from typing import Any, ParamSpec
from uuid import UUID
from unittest.mock import MagicMock

import inject
import pytest
from sqlalchemy.orm import sessionmaker, Session

from app.model import Person
from app.repository import PersonRepository
from app.service import PersonService
from gfmodules_python_shared.repository import T
from gfmodules_python_shared.repository.base import GenericRepository
from gfmodules_python_shared.session.session_manager import (
    get_repository,
    session_manager,
)

P = ParamSpec("P")
id_ = UUID("ce27130b-5449-4a3a-90db-57d96daf117b")


@pytest.fixture
def mock_inject(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[MagicMock, MagicMock]]:
    """
    Monkeypatch the instance function of the inject library.

    The patch is done within the context of the test evoking this fixture.

    yield:
        sessionmaker[Session] (MagicMock)
        Session (MagicMock)
    """
    session_maker = MagicMock(spec=sessionmaker)
    session = MagicMock(spec=Session)

    # mock sessionmaker's contextmanager
    session_maker.return_value.__enter__.return_value = session

    def close_session(*_: Any) -> None:
        session.close()

    session_maker.return_value.__exit__.side_effect = close_session

    # patch override the the instance function from the inject library
    # make sure the patch is done within context of the test evoking this fixture
    with monkeypatch.context() as mp:
        mp.setattr(
            inject,
            "instance",
            lambda cls: {sessionmaker[Session]: session_maker}[cls],
        )

        yield session_maker, session


def get_or_create(
    person_id: UUID, person_repository: PersonRepository = get_repository()
) -> Person:
    if person := person_repository.get(id=person_id):
        return person

    person_repository.create(Person(id=person_id, name="new person"))
    return person_repository.get_or_fail(id=person_id)


def is_repositories_instansiated(
    _: UUID,
    x_repository: PersonRepository = get_repository(),
    y_repository: PersonRepository = get_repository(),
) -> bool:
    return (
        isinstance(x_repository, PersonRepository)
        and isinstance(y_repository, PersonRepository)
        and x_repository != y_repository
    )


@pytest.mark.parametrize(
    "service, args, kwargs",
    (
        pytest.param(
            session_manager(lambda: True),
            (),
            {},
            id="no arguments",
        ),
        pytest.param(
            session_manager(lambda x: not issubclass(x, GenericRepository)),
            (int,),
            {},
            id="no repository arguments",
        ),
        pytest.param(
            session_manager(get_or_create),
            (),
            {"person_id": id_},
            id="function",
        ),
        pytest.param(
            PersonService().get_one,
            (id_,),
            {},
            id="method common usecase",
        ),
        pytest.param(
            session_manager(is_repositories_instansiated),
            (id_,),
            {},
            id="instantiate repositories",
        ),
    ),
)
def test_parameter_compositions(
    service: Callable[P, T],
    args: tuple[Any],
    kwargs: dict[str, Any],
    mock_inject: tuple[MagicMock, MagicMock],
) -> None:
    session_maker, session = mock_inject
    assert service(*args, **kwargs)  # pyright: ignore
    session_maker.assert_called_once()
    session.begin.assert_called_once()
    session.close.assert_called_once()


@pytest.mark.parametrize(
    "service, args, kwargs",
    (
        pytest.param(lambda: False, (), {}, id="no arguments"),
        pytest.param(
            lambda x: isinstance(x, GenericRepository),
            (int,),
            {},
            id="no repository arguments",
        ),
        pytest.param(
            is_repositories_instansiated, (id_,), {}, id="repositories not instantiated"
        ),
    ),
)
def test_no_decorator(
    service: Callable[P, T],
    args: tuple[Any],
    kwargs: dict[str, Any],
    mock_inject: tuple[MagicMock, MagicMock],
) -> None:
    session_maker, session = mock_inject
    assert not service(*args, **kwargs)  # pyright: ignore
    session_maker.assert_not_called()
    session.begin.assert_not_called()
    session.close.assert_not_called()


def test_no_repository_enstansiation() -> None:
    with pytest.raises(AttributeError, match=r"'NoneType' object has no attribute .*"):
        get_or_create(person_id=id_)
