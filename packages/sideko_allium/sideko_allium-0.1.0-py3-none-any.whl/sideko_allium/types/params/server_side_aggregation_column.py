import pydantic
import typing
import typing_extensions

from .server_side_aggregation_apply import (
    ServerSideAggregationApply,
    _SerializerServerSideAggregationApply,
)


class ServerSideAggregationColumn(typing_extensions.TypedDict):
    """
    ServerSideAggregationColumn
    """

    aggregate: typing_extensions.NotRequired[
        typing.Optional[
            typing_extensions.Literal["count", "max", "mean", "median", "min", "sum"]
        ]
    ]

    alias: typing_extensions.NotRequired[typing.Optional[str]]

    apply: typing_extensions.NotRequired[typing.Optional[ServerSideAggregationApply]]

    cast: typing_extensions.NotRequired[
        typing.Optional[
            typing_extensions.Literal[
                "bool", "decimal", "double", "float", "integer", "text", "timestamp"
            ]
        ]
    ]

    distinct: typing_extensions.NotRequired[typing.Optional[bool]]

    name: typing_extensions.Required[str]


class _SerializerServerSideAggregationColumn(pydantic.BaseModel):
    """
    Serializer for ServerSideAggregationColumn handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    aggregate: typing.Optional[
        typing_extensions.Literal["count", "max", "mean", "median", "min", "sum"]
    ] = pydantic.Field(alias="aggregate", default=None)
    alias: typing.Optional[str] = pydantic.Field(alias="alias", default=None)
    apply: typing.Optional[_SerializerServerSideAggregationApply] = pydantic.Field(
        alias="apply", default=None
    )
    cast: typing.Optional[
        typing_extensions.Literal[
            "bool", "decimal", "double", "float", "integer", "text", "timestamp"
        ]
    ] = pydantic.Field(alias="cast", default=None)
    distinct: typing.Optional[bool] = pydantic.Field(alias="distinct", default=None)
    name: str = pydantic.Field(
        alias="name",
    )
