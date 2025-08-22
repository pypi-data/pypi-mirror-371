import pydantic
import typing
import typing_extensions

from .query_config_parameters import QueryConfigParameters


class QueryConfig(pydantic.BaseModel):
    """
    QueryConfig
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    compute_profile: typing.Optional[str] = pydantic.Field(
        alias="compute_profile", default=None
    )
    datastore_to_use: typing.Optional[
        typing_extensions.Literal["gcs", "postgres", "snowflake"]
    ] = pydantic.Field(alias="datastore_to_use", default=None)
    limit: int = pydantic.Field(
        alias="limit",
    )
    parameters: typing.Optional[QueryConfigParameters] = pydantic.Field(
        alias="parameters", default=None
    )
    sql: str = pydantic.Field(
        alias="sql",
    )
