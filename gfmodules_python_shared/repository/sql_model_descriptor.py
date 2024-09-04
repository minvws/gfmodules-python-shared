from typing import TYPE_CHECKING, Any, Type, cast

from sqlalchemy.orm import DeclarativeBase

from gfmodules_python_shared.schema.sql_model import TSQLModel

if TYPE_CHECKING:
    from .base import GenericRepository


class ModelDescriptor:
    def __get__(
        self, obj: "GenericRepository[TSQLModel]", objtype: type | None = None
    ) -> Type[TSQLModel]:
        for base in getattr(objtype, "__orig_bases__", ()):
            if args := getattr(base, "__args__", None):
                return cast(
                    Type[TSQLModel],
                    next(arg for arg in args if issubclass(arg, DeclarativeBase)),
                )

        raise AttributeError(
            f"Unable to resolve the model type for {obj.__class__.__name__}."
        )

    def __set__(self, *_: Any) -> None:
        """This exists only to prevent write access"""
