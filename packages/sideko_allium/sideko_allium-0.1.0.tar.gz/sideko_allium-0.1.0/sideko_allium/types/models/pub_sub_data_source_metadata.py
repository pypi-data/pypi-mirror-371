import pydantic
import typing


class PubSubDataSourceMetadata(pydantic.BaseModel):
    """
    PubSubDataSourceMetadata
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    topic: str = pydantic.Field(
        alias="topic",
    )
    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
