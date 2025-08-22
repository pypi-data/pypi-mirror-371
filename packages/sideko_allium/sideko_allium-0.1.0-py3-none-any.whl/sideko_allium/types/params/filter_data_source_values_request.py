import pydantic
import typing
import typing_extensions


class FilterDataSourceValuesRequest(typing_extensions.TypedDict):
    """
    FilterDataSourceValuesRequest
    """

    operation: typing_extensions.Required[typing_extensions.Literal["ADD", "DELETE"]]

    values: typing_extensions.Required[typing.List[str]]


class _SerializerFilterDataSourceValuesRequest(pydantic.BaseModel):
    """
    Serializer for FilterDataSourceValuesRequest handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    operation: typing_extensions.Literal["ADD", "DELETE"] = pydantic.Field(
        alias="operation",
    )
    values: typing.List[str] = pydantic.Field(
        alias="values",
    )
