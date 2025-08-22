import pydantic
import typing
import typing_extensions

from .server_side_aggregation_column import (
    ServerSideAggregationColumn,
    _SerializerServerSideAggregationColumn,
)
from .server_side_aggregation_order import (
    ServerSideAggregationOrder,
    _SerializerServerSideAggregationOrder,
)

if typing_extensions.TYPE_CHECKING:
    from .data_filter import DataFilter, _SerializerDataFilter


class ServerSideAggregationConfig(typing_extensions.TypedDict):
    """
    ServerSideAggregationConfig
    """

    columns: typing_extensions.NotRequired[
        typing.Optional[typing.List[ServerSideAggregationColumn]]
    ]

    dataframe_name: typing_extensions.NotRequired[typing.Optional[str]]

    filters: typing_extensions.NotRequired[typing.Optional[typing.List["DataFilter"]]]

    limit: typing_extensions.NotRequired[typing.Optional[int]]

    offset: typing_extensions.NotRequired[typing.Optional[int]]

    order: typing_extensions.NotRequired[
        typing.Optional[typing.List[ServerSideAggregationOrder]]
    ]


class _SerializerServerSideAggregationConfig(pydantic.BaseModel):
    """
    Serializer for ServerSideAggregationConfig handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    columns: typing.Optional[typing.List[_SerializerServerSideAggregationColumn]] = (
        pydantic.Field(alias="columns", default=None)
    )
    dataframe_name: typing.Optional[str] = pydantic.Field(
        alias="dataframe_name", default=None
    )
    filters: typing.Optional[typing.List["_SerializerDataFilter"]] = pydantic.Field(
        alias="filters", default=None
    )
    limit: typing.Optional[int] = pydantic.Field(alias="limit", default=None)
    offset: typing.Optional[int] = pydantic.Field(alias="offset", default=None)
    order: typing.Optional[typing.List[_SerializerServerSideAggregationOrder]] = (
        pydantic.Field(alias="order", default=None)
    )
