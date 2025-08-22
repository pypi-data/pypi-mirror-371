import pydantic


class TokenInfo(pydantic.BaseModel):
    """
    TokenInfo
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = pydantic.Field(
        alias="name",
    )
    symbol: str = pydantic.Field(
        alias="symbol",
    )
