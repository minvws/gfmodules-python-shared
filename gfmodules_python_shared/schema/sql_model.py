from typing import Any, Iterator, TypeVar
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.exc import DetachedInstanceError


class SQLModelBase(DeclarativeBase):
    __abstract__ = True

    def __column_name_iter(
        self, exclude: set[str] | None = None, include: set[str] | None = None
    ) -> Iterator[str]:
        if include:
            return iter(include)
        columns = (column.name for column in self.__table__.columns)
        if exclude:
            return (column for column in columns if column not in exclude)
        return columns

    def to_dict(
        self, *, exclude: set[str] | None = None, include: set[str] | None = None
    ) -> dict[str, Any]:
        if exclude and include:
            raise ValueError("Either exclude or include not both")

        return {
            column: getattr(self, column)
            for column in self.__column_name_iter(exclude, include)
        }

    @staticmethod
    def __value_repr(value: Any) -> str:
        try:
            return str(value) if isinstance(value, UUID) else repr(value)
        except DetachedInstanceError:
            return "Not Loaded"

    def _repr(self, **fields: Any) -> str:
        """
        Helper function for _repr, inspired by:
        https://stackoverflow.com/questions/55713664/sqlalchemy-best-way-to-define-repr-for-large-tables
        """
        fields_ = (f"{key}={self.__value_repr(value)}" for key, value in fields.items())
        return f"{self.__class__.__name__}({', '.join(fields_)})"

    def __repr__(self) -> str:
        return self._repr(**self.to_dict())


TSQLModel = TypeVar("TSQLModel", bound=SQLModelBase)
