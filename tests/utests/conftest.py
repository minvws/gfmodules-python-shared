from collections.abc import Callable, Iterable, Iterator

import inject
import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.db import Database
from gfmodules_python_shared.schema.sql_model import SQLModelBase, TSQLModel


@pytest.fixture(scope="module", autouse=True)
def with_container() -> None:
    db = Database(dsn="sqlite:///:memory:", create_tables=True)
    inject.configure(
        lambda binder: binder.bind(Database, db).bind(  # type: ignore
            sessionmaker[Session], sessionmaker(db.engine)
        ),
        clear=True,
    )


@pytest.fixture(scope="module")
def session_maker() -> sessionmaker[Session]:
    return inject.instance(sessionmaker[Session])


@pytest.fixture
def session(session_maker: sessionmaker[Session]) -> Iterator[Session]:
    with session_maker() as session:
        yield session


@pytest.fixture(scope="module")
def insert_entities() -> Callable[[Session, Iterable[SQLModelBase]], None]:
    def inserter(
        session: Session,
        entities: Iterable[TSQLModel],
    ) -> None:
        with session.begin():
            session.bulk_save_objects(entities)

    return inserter
