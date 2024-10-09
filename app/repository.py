from typing import Any

from sqlalchemy.sql.expression import ColumnExpressionArgument

from app.model import Person
from gfmodules_python_shared.repository.base import RepositoryBase


class PersonRepository(RepositoryBase[Person]):
    @property
    def order_by(self) -> tuple[ColumnExpressionArgument[Any] | str, ...]:
        return (self.model.created_at,)
