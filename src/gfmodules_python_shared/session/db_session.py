import logging
from typing import Any, TypeVar, Sequence

from sqlalchemy import Engine, Select
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DbSession(object):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self.session = Session(self._engine, expire_on_commit=False)

    def __enter__(self) -> None:
        self.session.begin()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.session.close()

    def merge(self, entity: T) -> T:
        return self.session.merge(entity)

    def create(self, entity: T) -> None:
        try:
            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
        except DatabaseError as e:
            self.session.rollback()
            raise e

    def update(self, entity: T) -> None:
        try:
            self.session.commit()
            self.session.refresh(entity)
        except DatabaseError as e:
            self.session.rollback()
            raise e

    def delete(self, entity: T) -> None:
        try:
            self.session.delete(entity)
            self.session.commit()
        except DatabaseError as e:
            self.session.rollback()
            raise e

    def scalars_first(self, statement: Select[tuple[T]]) -> T | None:
        try:
            return self.session.scalars(statement).first()
        except DatabaseError as e:
            raise e

    def scalars_all(self, statement: Select[tuple[T]]) -> Sequence[T]:
        try:
            return self.session.scalars(statement).all()
        except DatabaseError as e:
            self.session.rollback()
            raise e

    def execute_scalar(self, statement: Select[tuple[T]]) -> Any | None:
        try:
            return self.session.execute(statement).scalar()
        except DatabaseError as e:
            self.session.rollback()
            raise e

