import pydantic
import typing
import typing_extensions

from .query_config import QueryConfig
from .query_run_results import QueryRunResults
from .query_run_stats import QueryRunStats


class QueryRun(pydantic.BaseModel):
    """
    QueryRun
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    completed_at: typing.Optional[str] = pydantic.Field(
        alias="completed_at", default=None
    )
    created_at: str = pydantic.Field(
        alias="created_at",
    )
    creator_id: str = pydantic.Field(
        alias="creator_id",
    )
    creator_org_team_user_id: typing.Optional[str] = pydantic.Field(
        alias="creator_org_team_user_id", default=None
    )
    creator_organization_id: typing.Optional[str] = pydantic.Field(
        alias="creator_organization_id", default=None
    )
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
    query_config: QueryConfig = pydantic.Field(
        alias="query_config",
    )
    query_id: str = pydantic.Field(
        alias="query_id",
    )
    queue_task_id: typing.Optional[str] = pydantic.Field(
        alias="queue_task_id", default=None
    )
    queued_at: typing.Optional[str] = pydantic.Field(alias="queued_at", default=None)
    results: typing.Optional[QueryRunResults] = pydantic.Field(
        alias="results", default=None
    )
    run_id: str = pydantic.Field(
        alias="run_id",
    )
    snowflake_query_id: typing.Optional[str] = pydantic.Field(
        alias="snowflake_query_id", default=None
    )
    source: typing.Optional[
        typing_extensions.Literal["api_server", "app_server", "workflow"]
    ] = pydantic.Field(alias="source", default=None)
    stats: typing.Optional[QueryRunStats] = pydantic.Field(alias="stats", default=None)
    status: typing_extensions.Literal[
        "canceled", "created", "failed", "queued", "running", "success"
    ] = pydantic.Field(
        alias="status",
    )
    zed_token: typing.Optional[str] = pydantic.Field(alias="zed_token", default=None)
