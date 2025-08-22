import pydantic
import typing

from .query_result_meta_column import QueryResultMetaColumn


class QueryResultMeta(pydantic.BaseModel):
    """
    QueryResultMeta
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    columns: typing.List[QueryResultMetaColumn] = pydantic.Field(
        alias="columns",
    )
    row_count: typing.Optional[int] = pydantic.Field(alias="row_count", default=None)
    run_id: typing.Optional[str] = pydantic.Field(alias="run_id", default=None)
