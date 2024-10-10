from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Generic, Iterable, List, Sequence, Type, TypeAlias, Union
from uuid import UUID

from more_itertools import unique_to_each
from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import ColumnExpressionArgument

from gfmodules_python_shared.repository.exceptions import EntryNotFound
from gfmodules_python_shared.schema.sql_model import TSQLModel

from .sql_model_descriptor import ModelDescriptor

GetKwargs: TypeAlias = Union[str, UUID, Dict[str, str]]


class GenericRepository(Generic[TSQLModel], metaclass=ABCMeta):
    model: Type[TSQLModel] = ModelDescriptor()  # type: ignore # lazy load model type at runtime

    def __init__(self, session: Session) -> None:
        self.session = session

    @property
    @abstractmethod
    def order_by(self) -> tuple[ColumnExpressionArgument[Any] | str, ...]:
        ...

    @abstractmethod
    def create(self, entity: TSQLModel) -> None:
        ...

    @abstractmethod
    def delete(self, entity: TSQLModel) -> None:
        ...

    @abstractmethod
    def get(self, **kwargs: GetKwargs) -> TSQLModel | None:
        ...

    def _scalars_all(self, statement: Select[tuple[TSQLModel]]) -> Sequence[TSQLModel]:
        return self.session.scalars(statement).all()


class RepositoryBase(GenericRepository[TSQLModel]):
    def create(self, entity: TSQLModel) -> None:
        self.session.add(entity)

    def delete(self, entity: TSQLModel) -> None:
        self.session.delete(entity)

    def get(self, **kwargs: GetKwargs) -> TSQLModel | None:
        self._validate_kwargs(**kwargs)
        stmt = select(self.model).filter_by(**kwargs)
        return self.session.scalars(stmt).first()

    def get_or_fail(self, **kwargs: GetKwargs) -> TSQLModel:
        if result := self.get(**kwargs):
            return result

        raise EntryNotFound(self.model)

    def get_many(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: Iterable[ColumnExpressionArgument[Any] | str] | None = None,
        **kwargs: GetKwargs,
    ) -> Sequence[TSQLModel]:
        self._validate_kwargs(**kwargs)

        order_by = self.order_by if order_by is None else [*self.order_by, *order_by]

        return self._scalars_all(
            select(self.model)
            .limit(limit=limit)
            .offset(offset=offset)
            .order_by(*order_by)
            .filter_by(**kwargs)
        )

    def count(self, **kwargs: GetKwargs) -> int:
        self._validate_kwargs(**kwargs)
        stmt = select(func.count()).select_from(self.model).filter_by(**kwargs)
        return self.session.execute(stmt).scalar() or 0

    def get_by_property(self, attribute: str, values: List[str]) -> Sequence[TSQLModel]:
        """
        Generates a chained OR condition based on the provided attribute values:
        eg: SELECT * FROM users WHERE users.email = :email_1 OR users.email = :email_2
        """
        if attribute not in self.model.__table__.columns.keys():  # noqa: SIM118
            raise AttributeError(
                f"{attribute} is not a column in the {self.model.__name__}"
            )
        return self._scalars_all(
            select(self.model).where(
                or_(*map(getattr(self.model, attribute).__eq__, values))
            )
        )

    def get_by_property_exact(
        self, attribute: str, values: List[str]
    ) -> Sequence[TSQLModel]:
        entities = self.get_by_property(attribute, values)

        if any(
            unique_to_each((getattr(entity, attribute) for entity in entities), values)
        ):
            raise EntryNotFound(self.model)

        return entities

    def _validate_kwargs(self, **kwargs: GetKwargs) -> None:
        # check if kwargs are a subset of column names for a given model
        if args := ", ".join(
            map(str, set(kwargs) - set(self.model.__table__.columns.keys()))
        ):
            raise InvalidRequestError(
                f"{args} is not a column in the {self.model.__name__}"
            )
