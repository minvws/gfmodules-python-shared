from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, Integer, String, types
from sqlalchemy.orm import Mapped, mapped_column

from gfmodules_python_shared.schema.sql_model import SQLModelBase


class Person(SQLModelBase):
    __tablename__ = "persons"

    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column("name", String(50), nullable=False, unique=True)
    age: Mapped[int] = mapped_column("age", Integer(), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP, nullable=False, default=datetime.now()
    )
