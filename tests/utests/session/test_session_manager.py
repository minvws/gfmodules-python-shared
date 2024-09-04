from collections.abc import Callable, Iterator
from typing import Any, ParamSpec, Type
from uuid import UUID
from unittest.mock import MagicMock, call

import inject
import pytest
from sqlalchemy.orm import sessionmaker, Session

from app.model import Person
from app.repository import PersonRepository
from app.service import PersonService
from gfmodules_python_shared.repository import T
from gfmodules_python_shared.repository.base import GenericRepository
from gfmodules_python_shared.repository.repository_factory import RepositoryFactory
from gfmodules_python_shared.session.session_manager import (
    get_repository,
    session_manager,
)

P = ParamSpec("P")


@pytest.fixture
def mock_inject(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[tuple[MagicMock, MagicMock, MagicMock]]:
    """
    Monkeypatch the instance function of the inject library.

    The patch is done within the context of the test evoking this fixture.

    yield:
        sessionmaker[Session] (MagicMock)
        Session (MagicMock)
        RepositoryFactory (MagicMock)
    """
    session_maker = MagicMock(spec=sessionmaker)
    session = MagicMock(spec=Session)
    repository_factory = MagicMock(spec=RepositoryFactory)

    # mock sessionmaker's contextmanager
    session_maker.return_value.__enter__.return_value = session

    def close_session(*_: Any) -> None:
        session.close()

    session_maker.return_value.__exit__.side_effect = close_session

    # mock the create method of RepositoryFactory
    def create_repository(
        repository_class: GenericRepository[T], _: Session
    ) -> MagicMock:
        return MagicMock(spec=repository_class)

    repository_factory.create.side_effect = create_repository

    # patch override the the instance function from the inject library
    # make sure the patch is done within context of the test evoking this fixture
    with monkeypatch.context() as mp:
        mp.setattr(
            inject,
            "instance",
            lambda cls: {
                sessionmaker[Session]: session_maker,
                RepositoryFactory: repository_factory,
            }[cls],
        )

        yield session_maker, session, repository_factory


id_ = UUID("ce27130b-5449-4a3a-90db-57d96daf117b")


def get_or_create(
    person_id: UUID, person_repository: PersonRepository = get_repository()
) -> Person:
    if person := person_repository.get(id=person_id):
        return person

    person_repository.create(Person(id=person_id, name="new person"))
    return person_repository.get_or_fail(id=person_id)


def multi_repository(
    _: UUID,
    x_repository: PersonRepository = get_repository(),
    y_repository: PersonRepository = get_repository(),
) -> bool:
    if x_repository is None:  # called without session_manager decorator
        return x_repository is y_repository
    return x_repository != y_repository


@pytest.mark.parametrize(
    "service, args, kwargs, expected_calls",
    (
        pytest.param(
            session_manager(lambda: True),
            (),
            {},
            (),
            id="no arguments",
        ),
        pytest.param(
            session_manager(lambda x: not issubclass(x, GenericRepository)),
            (int,),
            {},
            (),
            id="no repository arguments",
        ),
        pytest.param(
            session_manager(get_or_create),
            (),
            {"person_id": id_},
            (PersonRepository,),
            id="function",
        ),
        pytest.param(
            PersonService().get_one,
            (id_,),
            {},
            (PersonRepository,),
            id="method common usecase",
        ),
        pytest.param(
            session_manager(multi_repository),
            (id_,),
            {},
            (PersonRepository,) * 2,
            id="multiple repositories",
        ),
    ),
)
def test_parameter_compositions(
    service: Callable[P, T],
    args: tuple[Any],
    kwargs: dict[str, Any],
    expected_calls: tuple[Type[GenericRepository[T]]],
    mock_inject: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    session_maker, session, repository_factory = mock_inject
    assert service(*args, **kwargs)  # pyright: ignore
    session_maker.assert_called_once()
    # assert all Repository instances are
    assert repository_factory.create.call_args_list == [
        call(repository_class, session) for repository_class in expected_calls
    ]
    session.begin.assert_called_once()
    session.close.assert_called_once()


@pytest.mark.parametrize(
    "service, args, kwargs",
    (
        pytest.param(lambda: True, (), {}, id="no arguments"),
        pytest.param(
            lambda x: not issubclass(x, GenericRepository),
            (int,),
            {},
            id="no repository arguments",
        ),
        pytest.param(multi_repository, (id_,), {}, id="multiple repository arguments"),
    ),
)
def test_no_decorator(
    service: Callable[P, T],
    args: tuple[Any],
    kwargs: dict[str, Any],
    mock_inject: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    session_maker, session, repository_factory = mock_inject
    assert service(*args, **kwargs)  # pyright: ignore
    session_maker.assert_not_called()
    # assert all Repository instances are
    assert not repository_factory.create.call_args_list
    session.begin.assert_not_called()
    session.close.assert_not_called()


def test_no_repository_enstansiation() -> None:
    with pytest.raises(AttributeError, match=r"'NoneType' object has no attribute .*"):
        get_or_create(person_id=id_)
