import pydantic
import typing
import typing_extensions


class KafkaDataDestinationMetadata(typing_extensions.TypedDict):
    """
    KafkaDataDestinationMetadata
    """

    topic: typing_extensions.NotRequired[typing.Optional[str]]

    type_: typing_extensions.NotRequired[str]


class _SerializerKafkaDataDestinationMetadata(pydantic.BaseModel):
    """
    Serializer for KafkaDataDestinationMetadata handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    topic: typing.Optional[str] = pydantic.Field(alias="topic", default=None)
    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
