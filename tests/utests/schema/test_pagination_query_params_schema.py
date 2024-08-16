import pytest
from pydantic import ValidationError

from gfmodules_python_shared.schema.pagination.pagination_query_params_schema import PaginationQueryParams


def test_pagination_query_params_defaults() -> None:
    params = PaginationQueryParams()

    assert params.limit == 10
    assert params.offset == 0


def test_pagination_query_params_custom_values() -> None:
    params = PaginationQueryParams(limit=20, offset=5)

    assert params.limit == 20
    assert params.offset == 5


def test_pagination_query_params_invalid_limit() -> None:
    with pytest.raises(ValidationError) as excinfo:
        PaginationQueryParams(limit=0)
    assert "limit must be greater than 0" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        PaginationQueryParams(limit=-10)
    assert "limit must be greater than 0" in str(excinfo.value)


def test_pagination_query_params_invalid_offset() -> None:
    with pytest.raises(ValidationError) as excinfo:
        PaginationQueryParams(offset=-1)
    assert "offset must be greater than or equal to 0" in str(excinfo.value)
