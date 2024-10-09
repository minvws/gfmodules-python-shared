from pydantic import BaseModel

from gfmodules_python_shared.schema.pagination.page_schema import Page


class User(BaseModel):
    id: int
    name: str


def test_page_schema() -> None:
    users = [User(id=1, name="John Doe"), User(id=2, name="Jane Smith")]

    user_page = Page[User](items=users, limit=10, offset=0, total=50)

    assert len(user_page.items) == 2
    assert user_page.items[0].name == "John Doe"
    assert user_page.items[1].name == "Jane Smith"
    assert user_page.limit == 10
    assert user_page.offset == 0
    assert user_page.total == 50

    json_data = user_page.model_dump_json()
    expected_json = (
        '{"items":[{"id":1,"name":"John Doe"},{"id":2,"name":"Jane Smith"}],'
        '"limit":10,"offset":0,"total":50}'
    )
    assert json_data == expected_json
