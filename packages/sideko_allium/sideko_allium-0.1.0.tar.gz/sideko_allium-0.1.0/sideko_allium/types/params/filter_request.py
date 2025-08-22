import pydantic
import typing
import typing_extensions


class FilterRequest(typing_extensions.TypedDict):
    """
    FilterRequest
    """

    filter: typing_extensions.Required[typing.Dict[str, typing.Any]]

    id: typing_extensions.NotRequired[typing.Optional[str]]

    organization_id: typing_extensions.NotRequired[typing.Optional[str]]


class _SerializerFilterRequest(pydantic.BaseModel):
    """
    Serializer for FilterRequest handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    filter: typing.Dict[str, typing.Any] = pydantic.Field(
        alias="filter",
    )
    id: typing.Optional[str] = pydantic.Field(alias="id", default=None)
    organization_id: typing.Optional[str] = pydantic.Field(
        alias="organization_id", default=None
    )
