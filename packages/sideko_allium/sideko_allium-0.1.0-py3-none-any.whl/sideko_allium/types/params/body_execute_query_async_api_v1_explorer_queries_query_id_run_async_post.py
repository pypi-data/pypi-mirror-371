import pydantic
import typing
import typing_extensions

from .body_execute_query_async_api_v1_explorer_queries_query_id_run_async_post_parameters import (
    BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters,
    _SerializerBodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters,
)
from .query_run_request_config import (
    QueryRunRequestConfig,
    _SerializerQueryRunRequestConfig,
)


class BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPost(
    typing_extensions.TypedDict
):
    """
    BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPost
    """

    parameters: typing_extensions.Required[
        typing.Optional[
            BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters
        ]
    ]

    run_config: typing_extensions.NotRequired[QueryRunRequestConfig]


class _SerializerBodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPost(
    pydantic.BaseModel
):
    """
    Serializer for BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPost handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    parameters: typing.Optional[
        _SerializerBodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters
    ] = pydantic.Field(
        alias="parameters",
    )
    run_config: typing.Optional[_SerializerQueryRunRequestConfig] = pydantic.Field(
        alias="run_config", default=None
    )
