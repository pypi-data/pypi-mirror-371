import pydantic
import typing
import typing_extensions


class QueryRunStats(pydantic.BaseModel):
    """
    QueryRunStats
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    data_size_bytes: typing.Optional[int] = pydantic.Field(
        alias="data_size_bytes", default=None
    )
    datastore: typing.Optional[
        typing_extensions.Literal["gcs", "postgres", "snowflake"]
    ] = pydantic.Field(alias="datastore", default=None)
    end_time: str = pydantic.Field(
        alias="end_time",
    )
    row_count: typing.Optional[int] = pydantic.Field(alias="row_count", default=None)
    snowflake_query_stats: typing.Optional[typing.Dict[str, typing.Any]] = (
        pydantic.Field(alias="snowflake_query_stats", default=None)
    )
    sql: typing.Optional[str] = pydantic.Field(alias="sql", default=None)
    start_time: str = pydantic.Field(
        alias="start_time",
    )
