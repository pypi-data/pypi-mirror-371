import pydantic
import typing_extensions


class QueryRunResults(pydantic.BaseModel):
    """
    QueryRunResults
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    storage_type: typing_extensions.Literal["gcs"] = pydantic.Field(
        alias="storage_type",
    )
