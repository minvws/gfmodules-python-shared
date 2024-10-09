from typing import Any
from uuid import UUID, uuid4

import pytest
from sqlalchemy import ColumnExpressionArgument, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gfmodules_python_shared.repository.base import RepositoryBase
from gfmodules_python_shared.schema.sql_model import SQLModelBase
from gfmodules_python_shared.session.session_manager import (
    get_repository,
    session_manager,
)
from tests.utests.utils import are_the_same_entity


# entities
class Post(SQLModelBase):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column("id", primary_key=True, default=uuid4)
    message: Mapped[str] = mapped_column("message", nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))


class User(SQLModelBase):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column("id", primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column("name", String(50), nullable=False, unique=True)
    posts: Mapped[list[Post]] = relationship(
        lazy="selectin",
        cascade="all, delete, delete-orphan",
    )


# repository
class UserRepository(RepositoryBase[User]):
    @property
    def order_by(self) -> tuple[ColumnExpressionArgument[Any] | str, ...]:
        return (User.name.desc(),)


# services
@session_manager
def get_user(
    user_id: UUID, *, user_repository: UserRepository = get_repository()
) -> User:
    return user_repository.get_or_fail(id=user_id)


@session_manager
def username_exists(
    name: str, *, user_repository: UserRepository = get_repository()
) -> bool:
    return bool(user_repository.get_by_property("name", [name]))


@session_manager
def add_user(name: str, *, user_repository: UserRepository = get_repository()) -> User:
    if username_exists(name):
        raise ValueError(f"Name already in use: {name}")
    user = User(name=name)
    user_repository.create(user)
    return user


@session_manager
def remove_user(
    user_id: UUID, *, user_repository: UserRepository = get_repository()
) -> User:
    user = get_user(user_id, user_repository=user_repository)
    user_repository.delete(user)
    return user


@session_manager
def add_post(
    user_id: UUID, message: str, *, user_repository: UserRepository = get_repository()
) -> list[Post]:
    user = user_repository.get_or_fail(id=user_id)
    post = Post(message=message)
    user.posts.append(post)
    return user.posts


@session_manager
def remove_post(
    user_id: UUID, post_id: UUID, *, user_repository: UserRepository = get_repository()
) -> list[Post]:
    user = user_repository.get_or_fail(id=user_id)
    user.posts.remove(next(post for post in user.posts if post.id == post_id))
    return user.posts


@pytest.fixture
def user() -> User:
    return add_user("a name")


def test_user_presists_in_db_when_add_user() -> None:
    assert add_user("some name").id


def test_remove_user_from_db_and_give_non_presisted_python_object(user: User) -> None:
    assert are_the_same_entity(user, remove_user(user.id))


def test_user_post_presists_in_db_when_users_posts_modified(user: User) -> None:
    message = "a short message"
    assert add_post(user.id, message)
    post, *_ = get_user(user.id).posts
    assert post and post.message == message
    remove_post(user.id, post.id)
    assert not get_user(user.id).posts
