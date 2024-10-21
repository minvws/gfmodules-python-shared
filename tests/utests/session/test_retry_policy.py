from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import DatabaseError, OperationalError
from sqlalchemy.orm import Session

from gfmodules_python_shared.session.session_manager import (
    service_transaction_retry_policy,
)


@pytest.fixture
def mock_session() -> MagicMock:
    return MagicMock(spec=Session)


@pytest.fixture
def mock_service() -> MagicMock:
    def some_function() -> None: ...

    return MagicMock(spec=some_function)


operational_error = OperationalError(None, None, Exception())


@pytest.mark.parametrize(
    "side_effects, call_count",
    (
        pytest.param(["Success"], 1, id="happy path"),
        pytest.param([operational_error, "Success"], 2, id="single operational error"),
        pytest.param(
            [DatabaseError(None, None, Exception()), "Success"],
            2,
            id="single database error",
        ),
        pytest.param(
            [AttributeError, ValueError, "Success"], 3, id="two generic errors"
        ),
    ),
)
def test_service_transaction_retry_policy_success(
    side_effects: list[Exception | str],
    call_count: int,
    mock_session: MagicMock,
    mock_service: MagicMock,
) -> None:
    mock_service.side_effect = side_effects

    result = service_transaction_retry_policy(mock_session, mock_service)

    assert mock_service.call_count == call_count
    assert result == "Success"


def test_service_transaction_retry_policy_failure(
    mock_session: MagicMock, mock_service: MagicMock
) -> None:
    mock_service.side_effect = operational_error

    with pytest.raises(RuntimeError, match="failed after 3 retries"):
        service_transaction_retry_policy(mock_session, mock_service)

    assert mock_service.call_count == 3
