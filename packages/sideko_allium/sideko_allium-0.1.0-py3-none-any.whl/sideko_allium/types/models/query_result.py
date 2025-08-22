import pydantic
import typing

from .query_result_meta import QueryResultMeta


class QueryResult(pydantic.BaseModel):
    """
    QueryResult
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    data: typing.Optional[typing.Any] = pydantic.Field(alias="data", default=None)
    meta: QueryResultMeta = pydantic.Field(
        alias="meta",
    )
    queried_at: typing.Optional[str] = pydantic.Field(alias="queried_at", default=None)
    sql: str = pydantic.Field(
        alias="sql",
    )
