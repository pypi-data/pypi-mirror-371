import pydantic
import typing
import typing_extensions


class QueryRunRequestConfig(typing_extensions.TypedDict):
    """
    QueryRunRequestConfig
    """

    limit: typing_extensions.NotRequired[typing.Optional[int]]


class _SerializerQueryRunRequestConfig(pydantic.BaseModel):
    """
    Serializer for QueryRunRequestConfig handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    limit: typing.Optional[int] = pydantic.Field(alias="limit", default=None)
