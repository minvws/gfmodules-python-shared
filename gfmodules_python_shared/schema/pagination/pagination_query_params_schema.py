from typing import Annotated

from fastapi import Query

from gfmodules_python_shared.schema.base_model_schema import BaseModelConfig


class PaginationQueryParams(BaseModelConfig):
    limit: Annotated[int, Query(gt=0)] = 10
    offset: Annotated[int, Query(ge=0)] = 0
