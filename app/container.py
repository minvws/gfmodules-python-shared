import inject
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def container_config(binder: inject.Binder) -> None:
    binder.bind(
        sessionmaker[Session],
        sessionmaker(create_engine("sqlite:///:memory:", echo=False)),
    )
