import pydantic


class FilterDataSourceValuesResponse(pydantic.BaseModel):
    """
    FilterDataSourceValuesResponse
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    message: str = pydantic.Field(
        alias="message",
    )
