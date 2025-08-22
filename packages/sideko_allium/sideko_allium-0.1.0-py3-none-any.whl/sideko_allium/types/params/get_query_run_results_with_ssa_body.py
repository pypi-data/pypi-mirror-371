import pydantic
import typing
import typing_extensions


if typing_extensions.TYPE_CHECKING:
    from .server_side_aggregation_config import (
        ServerSideAggregationConfig,
        _SerializerServerSideAggregationConfig,
    )


class GetQueryRunResultsWithSsaBody(typing_extensions.TypedDict):
    """
    GetQueryRunResultsWithSsaBody
    """

    config: typing_extensions.NotRequired[
        typing.Optional["ServerSideAggregationConfig"]
    ]


class _SerializerGetQueryRunResultsWithSsaBody(pydantic.BaseModel):
    """
    Serializer for GetQueryRunResultsWithSsaBody handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    config: typing.Optional["_SerializerServerSideAggregationConfig"] = pydantic.Field(
        alias="config", default=None
    )
