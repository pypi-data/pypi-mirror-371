import pydantic
import typing
import typing_extensions


class PubSubDataDestinationMetadata(pydantic.BaseModel):
    """
    PubSubDataDestinationMetadata
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
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
