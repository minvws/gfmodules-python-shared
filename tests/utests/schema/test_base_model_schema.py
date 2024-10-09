from typing import Optional

from gfmodules_python_shared.schema.base_model_schema import BaseModelConfig


class NewModel(BaseModelConfig):
    some_field: str
    another_field: Optional[int]


def test_base_model_config() -> None:
    model_instance = NewModel(some_field="test value", another_field=123)

    assert model_instance.some_field == "test value"
    assert model_instance.another_field == 123


def test_base_model_config_create_by_field_alias() -> None:
    model_instance = NewModel(  # type: ignore
        someField="test value", anotherField=123
    )

    assert model_instance.some_field == "test value"
    assert model_instance.another_field == 123


def test_base_model_config_json_output() -> None:
    model_instance = NewModel(some_field="test value", another_field=123)

    json_data = model_instance.model_dump_json()
    expected_json = '{"some_field":"test value","another_field":123}'
    assert json_data == expected_json

    json_data = model_instance.model_dump_json(by_alias=True)
    expected_json = '{"someField":"test value","anotherField":123}'
    assert json_data == expected_json
