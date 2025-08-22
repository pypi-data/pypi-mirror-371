import pydantic


class FilterDataSourceResponse(pydantic.BaseModel):
    """
    FilterDataSourceResponse
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    description: str = pydantic.Field(
        alias="description",
    )
    id: str = pydantic.Field(
        alias="id",
    )
    name: str = pydantic.Field(
        alias="name",
    )
    type_: str = pydantic.Field(
        alias="type",
    )
