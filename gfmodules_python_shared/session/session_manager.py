from functools import wraps
import inspect
import inject

from typing import Callable, TypeVar, ParamSpec, Any

from sqlalchemy.orm import Session, sessionmaker

from gfmodules_python_shared.repository.base import GenericRepository
from gfmodules_python_shared.repository.repository_factory import RepositoryFactory


T = TypeVar("T")
P = ParamSpec("P")


# needs changing
def get_repository() -> Any:
    return None


def session_manager(func: Callable[P, T]) -> Callable[P, T]:
    """
    This decorator requests, injects and cleans your session for the given service operation context.

    The session is encapsulated by this decorator, thus will not be exposed to the service operation.

    Use of type annotation is vital, GenericRepository subclass parameters are instantiated with the requested session, and injected in the service operation signature
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        repository_factory = inject.instance(RepositoryFactory)
        session_maker = inject.instance(sessionmaker[Session])

        with session_maker() as session:
            kwargs |= { # type: ignore
                parameter.name: repository_factory.create(parameter.annotation, session)
                for parameter in inspect.signature(func).parameters.values()
                if issubclass(parameter.annotation, GenericRepository)
            }
            with session.begin():
                return func(*args, **kwargs)

    return wrapper
