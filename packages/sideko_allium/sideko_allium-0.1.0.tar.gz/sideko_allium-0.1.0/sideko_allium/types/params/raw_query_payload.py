import pydantic
import typing_extensions


class RawQueryPayload(typing_extensions.TypedDict):
    """
    RawQueryPayload
    """

    query: typing_extensions.Required[str]


class _SerializerRawQueryPayload(pydantic.BaseModel):
    """
    Serializer for RawQueryPayload handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    query: str = pydantic.Field(
        alias="query",
    )
