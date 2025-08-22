import pydantic
import typing_extensions


class ServerSideAggregationOrder(typing_extensions.TypedDict):
    """
    ServerSideAggregationOrder
    """

    direction: typing_extensions.Required[typing_extensions.Literal["asc", "desc"]]

    name: typing_extensions.Required[str]


class _SerializerServerSideAggregationOrder(pydantic.BaseModel):
    """
    Serializer for ServerSideAggregationOrder handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    direction: typing_extensions.Literal["asc", "desc"] = pydantic.Field(
        alias="direction",
    )
    name: str = pydantic.Field(
        alias="name",
    )
