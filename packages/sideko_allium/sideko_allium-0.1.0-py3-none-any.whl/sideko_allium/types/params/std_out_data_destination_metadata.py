import pydantic
import typing
import typing_extensions


class StdOutDataDestinationMetadata(typing_extensions.TypedDict):
    """
    StdOutDataDestinationMetadata
    """

    type_: typing_extensions.NotRequired[str]


class _SerializerStdOutDataDestinationMetadata(pydantic.BaseModel):
    """
    Serializer for StdOutDataDestinationMetadata handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
