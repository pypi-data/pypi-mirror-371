import pydantic
import typing
import typing_extensions


class PubSubDataDestinationMetadata(typing_extensions.TypedDict):
    """
    PubSubDataDestinationMetadata
    """

    delivery_type: typing_extensions.NotRequired[
        typing_extensions.Literal["PULL", "PUSH"]
    ]

    subscription: typing_extensions.NotRequired[typing.Optional[str]]

    topic: typing_extensions.NotRequired[typing.Optional[str]]

    type_: typing_extensions.NotRequired[str]

    webhook_url: typing_extensions.NotRequired[typing.Optional[str]]


class _SerializerPubSubDataDestinationMetadata(pydantic.BaseModel):
    """
    Serializer for PubSubDataDestinationMetadata handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    delivery_type: typing.Optional[typing_extensions.Literal["PULL", "PUSH"]] = (
        pydantic.Field(alias="delivery_type", default=None)
    )
    subscription: typing.Optional[str] = pydantic.Field(
        alias="subscription", default=None
    )
    topic: typing.Optional[str] = pydantic.Field(alias="topic", default=None)
    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
    webhook_url: typing.Optional[str] = pydantic.Field(
        alias="webhook_url", default=None
    )
