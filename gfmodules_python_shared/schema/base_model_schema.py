from pydantic import BaseModel, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel


class BaseModelConfig(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            alias=to_camel,
        ),
        populate_by_name=True
    )
