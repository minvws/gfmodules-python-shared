from pydantic import field_validator

from gfmodules_python_shared.schema.base_model_schema import BaseModelConfig


class PaginationQueryParams(BaseModelConfig):
    limit: int = 10
    offset: int = 0

    @field_validator("limit")
    def validate_limit(cls, limit: int) -> int:
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        return limit

    @field_validator("offset")
    def validate_offset(cls, offset: int) -> int:
        if offset < 0:
            raise ValueError("offset must be greater than or equal to 0")

        return offset
