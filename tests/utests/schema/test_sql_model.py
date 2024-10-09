from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy.orm import Mapped, mapped_column
from typing_extensions import override

from gfmodules_python_shared.schema.sql_model import SQLModelBase


class Model(SQLModelBase):
    __tablename__ = "models"

    id: Mapped[UUID] = mapped_column("id", primary_key=True)
    name: Mapped[str]
    age: Mapped[int]
    time: Mapped[datetime]


@pytest.fixture(scope="module")
def model_id() -> UUID:
    return UUID("225fa1a1-8e18-42ef-8fd4-d80c433f8ee1")


@pytest.fixture(scope="module")
def time() -> datetime:
    return datetime.now()


@pytest.fixture(scope="module")
def model(model_id: UUID, time: datetime) -> Model:
    return Model(id=model_id, name="some name", age=11, time=time)


def test_repr(model: Model, model_id: UUID, time: datetime) -> None:
    assert (
        repr(model) == f"Model(id={model_id}, name='some name', age=11, time={time!r})"
    )


def test_to_dict_bad_use(model: Model) -> None:
    with pytest.raises(ValueError, match="Either exclude or include not both"):
        model.to_dict(exclude={"does not matter"}, include={"also does not matter"})


def test_overide_repr_exclude_id(model_id: UUID, time: datetime) -> None:
    class NoIDModel(SQLModelBase):
        __tablename__ = "no_id_models"

        id: Mapped[UUID] = mapped_column("id", primary_key=True)
        name: Mapped[str]
        age: Mapped[int]
        time: Mapped[datetime]

        @override
        def __repr__(self) -> str:
            return self._repr(**self.to_dict(exclude={"id"}))

    model = NoIDModel(id=model_id, name="some name", age=11, time=time)
    assert repr(model) == f"NoIDModel(name='some name', age=11, time={time!r})"


def test_overide_repr_include_name(model_id: UUID, time: datetime) -> None:
    class NamedModel(SQLModelBase):
        __tablename__ = "named_models"

        id: Mapped[UUID] = mapped_column("id", primary_key=True)
        name: Mapped[str] = mapped_column("name", unique=True)
        age: Mapped[int]
        time: Mapped[datetime]

        @override
        def __repr__(self) -> str:
            return self._repr(**self.to_dict(include={"name"}))

    model = NamedModel(id=model_id, name="some name", age=11, time=time)
    assert repr(model) == "NamedModel(name='some name')"
