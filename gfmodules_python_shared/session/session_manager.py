import inspect
import inject
from functools import cache

from typing import Callable, TypeVar, ParamSpec, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from gfmodules_python_shared.repository.base import RepositoryBase
from gfmodules_python_shared.repository.repository_factory import RepositoryFactory


T = TypeVar("T")
P = ParamSpec("P")


# needs changing
def get_repository() -> Any:
    return None

@cache
def get_session_factory(dsn: str = "sqlite:///:memory:") -> sessionmaker[Session]:
    return sessionmaker(create_engine(dsn),expire_on_commit=True)


def session_manager(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(self: ParamSpec, *args: P.args, **kwargs: P.kwargs) -> T:
        signature = inspect.signature(func)

        repository_factory = inject.instance(RepositoryFactory)

        func_args: P.args = {}

        params_list = [p for p in signature.parameters.values() if p.name != "self"]
        for arg, param in zip(args, params_list[: len(args)]):
            func_args[param.name] = arg


        with get_session_factory()() as session:
            for p in signature.parameters.values():
                # copy self param to func_args if present
                if p.name == "self":
                    func_args[p.name] = self
                    continue

                # Ignore param if already in kwargs
                if p.name in kwargs:
                    func_args[p.name] = kwargs[p.name]
                    continue

                # Ignore param if already handled in args
                if p.name in func_args:
                    continue

                # Copy supplied None value to func_args
                if p.annotation is inspect.Parameter.empty:
                    func_args[p.name] = None
                    continue

                # Ignore anything that is not a repositoryBase
                if not issubclass(p.annotation, RepositoryBase):
                    continue
                func_args[p.name] = repository_factory.create(p.annotation, session)

            # Handle actual function inside session context
            return func(**func_args)

    return wrapper  # type: ignore
