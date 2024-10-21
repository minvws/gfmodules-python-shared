import inspect
import logging
import random
from collections.abc import Callable, Sequence
from functools import wraps
from time import sleep
from typing import Any, ParamSpec, TypeVar

import inject
from sqlalchemy.exc import DatabaseError, OperationalError
from sqlalchemy.orm import DeclarativeBase, Session, attributes, sessionmaker

from gfmodules_python_shared.repository.base import GenericRepository

T = TypeVar("T")
P = ParamSpec("P")
logger = logging.getLogger(__name__)


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


def service_transaction_retry_policy(
    session: Session,
    service: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    # TODO: pull backoffs from config
    # inject.instance(Config).database.backoffs
    backoffs = [0.1, 0.2, 0.4]
    for backoff in backoffs:
        try:
            with session.begin():
                return service(*args, **kwargs)
        except (OperationalError, DatabaseError, Exception) as e:
            logger.warning(
                f"Retrying transaction operation due to {e.__class__.__name__}: {e}"
            )
        logger.info(f"Retrying {service} in {backoff} seconds")
        sleep(backoff + random.uniform(0, 0.1))
    raise RuntimeError(
        f"Transaction '{service.__name__}' failed after {len(backoffs)} retries"
    )


def session_manager(service: Callable[P, T]) -> Callable[P, T]:
    """
    This decorator requests, injects and cleans your session for the given service
    operation context.

    The session is encapsulated by this decorator, thus will not be exposed to the
    service operation. Use of type annotation is vital, GenericTepository subclass
    parameters are instantiated with the requested session, and injected in the service
    operation signature.

    Failed transaction will be retried according to the service transaction retry policy
    If transaction is still unsuccessful after all retry, then a runtime error is raised

    return value is synced with the database before sent to caller.
    """

    @wraps(service)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with inject.instance(sessionmaker[Session])() as session:
            kwargs |= {  # type: ignore
                parameter.name: parameter.annotation(session)
                for parameter in inspect.signature(service).parameters.values()
                if inspect.isclass(parameter.annotation)
                and issubclass(parameter.annotation, GenericRepository)
                and parameter.default is None
            }
            value = service_transaction_retry_policy(session, service, *args, **kwargs)
            sync_value_with_database(session, value)
        return value

    return wrapper
