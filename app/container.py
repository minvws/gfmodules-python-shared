import inject
from sqlalchemy.orm import Session, sessionmaker

from app.db import Database


def container_config(binder: inject.Binder) -> None:
    db = Database(dsn="sqlite:///:memory:")
    binder.bind(Database, db)
    binder.bind(sessionmaker[Session], sessionmaker(db.engine))

