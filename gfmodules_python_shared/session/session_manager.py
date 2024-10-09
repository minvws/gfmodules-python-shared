import inspect
from collections.abc import Sequence
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

import inject
from sqlalchemy.orm import DeclarativeBase, Session, attributes, sessionmaker

from gfmodules_python_shared.repository.base import GenericRepository

T = TypeVar("T")
P = ParamSpec("P")


# needs changing
def get_repository() -> Any:
    return None


def sync_value_with_database(session: Session, value: Any) -> None:
    if isinstance(value, DeclarativeBase) and session.identity_map.contains_state(
        attributes.instance_state(value)
    ):
        session.refresh(value)
    elif isinstance(value, Sequence):
        for e in value:
            sync_value_with_database(session, e)


def session_manager(service: Callable[P, T]) -> Callable[P, T]:
    """
    This decorator requests, injects and cleans your session for the given service
    operation context.

    The session is encapsulated by this decorator, thus will not be exposed to the
    service operation. Use of type annotation is vital, GenericTepository subclass
    parameters are instantiated with the requested session, and injected in the service
    operation signature.

    return value is synced with the database before sent to caller.
    """

    @wraps(service)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        session_maker = inject.instance(sessionmaker[Session])

        with session_maker() as session:
            kwargs |= {  # type: ignore
                parameter.name: parameter.annotation(session)
                for parameter in inspect.signature(service).parameters.values()
                if inspect.isclass(parameter.annotation)
                and issubclass(parameter.annotation, GenericRepository)
                and parameter.default is None
            }
            with session.begin():
                value = service(*args, **kwargs)
            sync_value_with_database(session, value)
        return value

    return wrapper
