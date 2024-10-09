from typing import Generic, List, TypeVar

from gfmodules_python_shared.schema.base_model_schema import BaseModelConfig

T = TypeVar("T")


class Page(BaseModelConfig, Generic[T]):
    """
    Schema for pagination of entities in the application.
    """

    items: List[T]
    limit: int
    offset: int
    total: int
