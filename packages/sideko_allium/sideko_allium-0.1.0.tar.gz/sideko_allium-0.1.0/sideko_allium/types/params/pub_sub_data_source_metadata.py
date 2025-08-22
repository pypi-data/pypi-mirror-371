import pydantic
import typing
import typing_extensions


class PubSubDataSourceMetadata(typing_extensions.TypedDict):
    """
    PubSubDataSourceMetadata
    """

    topic: typing_extensions.Required[str]

    type_: typing_extensions.NotRequired[str]


class _SerializerPubSubDataSourceMetadata(pydantic.BaseModel):
    """
    Serializer for PubSubDataSourceMetadata handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    topic: str = pydantic.Field(
        alias="topic",
    )
    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
