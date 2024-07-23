from uuid import UUID, uuid4

from sqlalchemy import String, types
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        primary_key=True,
        nullable=False,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column("name", String(50), nullable=False, unique=True)
