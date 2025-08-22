import pydantic


class QueryResultMetaColumn(pydantic.BaseModel):
    """
    QueryResultMetaColumn
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    data_type: str = pydantic.Field(
        alias="data_type",
    )
    name: str = pydantic.Field(
        alias="name",
    )
