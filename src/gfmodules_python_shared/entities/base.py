from typing import TypeVar, Dict, Any

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.exc import DetachedInstanceError


class Base(DeclarativeBase):

    def to_dict(self) -> Dict[str, Any]:
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}

    def _repr(self, **fields: Any) -> str:
        """
        Helper function for _repr, inspired by:
        https://stackoverflow.com/questions/55713664/sqlalchemy-best-way-to-define-repr-for-large-tables
        """
        field_strings = []
        for key, value in fields.items():
            try:
                field_strings.append(f"{key}={value!r}")
            except DetachedInstanceError:
                field_strings.append(f"{key}=Not Loaded")

        return f"{self.__class__.__name__}({', '.join(field_strings)})"


TBase = TypeVar("TBase", bound=Base, covariant=True)
