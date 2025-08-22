import pydantic
import typing_extensions


class FilterDataSourceRequest(typing_extensions.TypedDict):
    """
    FilterDataSourceRequest
    """

    description: typing_extensions.Required[str]

    name: typing_extensions.Required[str]

    type_: typing_extensions.Required[str]


class _SerializerFilterDataSourceRequest(pydantic.BaseModel):
    """
    Serializer for FilterDataSourceRequest handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    description: str = pydantic.Field(
        alias="description",
    )
    name: str = pydantic.Field(
        alias="name",
    )
    type_: str = pydantic.Field(
        alias="type",
    )
