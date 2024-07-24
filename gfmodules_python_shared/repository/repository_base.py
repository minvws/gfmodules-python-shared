from abc import ABC, abstractmethod
from typing import TypeVar, Union, Dict, Generic, Sequence, List, Type
from uuid import UUID

from sqlalchemy import select, or_, func
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import DeclarativeBase

from gfmodules_python_shared.repository.exceptions import EntryNotFound
from gfmodules_python_shared.session.db_session import DbSession
from gfmodules_python_shared.utils.validators import validate_sets_equal

T = TypeVar("T", bound=DeclarativeBase)

TArgs = TypeVar("TArgs", bound=Union[str, UUID, Dict[str, str]])


class GenericRepository(Generic[T], ABC):
    def __init__(self, session: DbSession):
        self.session = session

    @abstractmethod
    def create(self, entity: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, **kwargs: TArgs) -> T | None:
        raise NotImplementedError


class RepositoryBase(GenericRepository[T], ABC):
    def __init__(self, session: DbSession, cls_model: Type[T]) -> None:
        super().__init__(session)
        self.model = cls_model

    def create(self, entity: T) -> None:
        return self.session.create(entity)

    def update(self, entity: T) -> None:
        return self.session.update(entity)

    def delete(self, entity: T) -> None:
        return self.session.delete(entity)

    def get(self, **kwargs: TArgs) -> T | None:
        self._validate_kwargs(**kwargs)
        stmt = select(self.model).filter_by(**kwargs)
        return self.session.scalars_first(stmt)

    def get_or_fail(self, **kwargs: TArgs) -> T:
        self._validate_kwargs(**kwargs)
        result = self.get(**kwargs)
        if result is None:
            raise EntryNotFound(self.model)

        return result

    def get_many(
        self, limit: int | None = None, offset: int | None = None, **kwargs: TArgs
    ) -> Sequence[T]:
        self._validate_kwargs(**kwargs)
        stmt = (
            select(self.model)
            .limit(limit=limit)
            .offset(offset=offset)
            .order_by("created_at")
            .filter_by(**kwargs)
        )
        return self.session.scalars_all(stmt)

    def count(self, **kwargs: TArgs) -> int:
        self._validate_kwargs(**kwargs)
        stmt = select(func.count()).select_from(self.model).filter_by(**kwargs)
        result = self.session.execute_scalar(stmt)
        if isinstance(result, int) and not None:
            return result

        raise TypeError(f"{result} is not an integer")

    def get_by_property(self, attribute: str, values: List[str]) -> Sequence[T]:
        """
        Generates a chained OR condition based on the provided attribute values:
        eg: SELECT * FROM users WHERE users.email = :email_1 OR users.email = :email_2
        """
        if attribute not in self.model.__table__.columns.keys():
            raise AttributeError(
                f"{attribute} is not a column in the {self.model.__name__}"
            )

        conditions = [getattr(self.model, attribute).__eq__(value) for value in values]
        stmt = select(self.model).where(or_(*conditions))

        return self.session.scalars_all(stmt)

    def get_by_property_exact(self, attribute: str, values: List[str]) -> Sequence[T]:
        results = self.get_by_property(attribute, values)
        result_values = [getattr(result, attribute) for result in results]
        valid_results = validate_sets_equal(result_values, values)

        if not valid_results:
            raise EntryNotFound(self.model)

        return results

    def _validate_kwargs(self, **kwargs: TArgs) -> None:
        # check if kwargs are a subset of column names for a given model
        if not issubclass(self.model, DeclarativeBase):
            raise TypeError(f"Model {self.model} is not a subclass of Declarative Base")

        if not (set([*kwargs]) <= set([*self.model.__table__.columns.keys()])):
            raise InvalidRequestError(
                f"{[*kwargs]} is not a column in the {self.model.__name__}"
            )
