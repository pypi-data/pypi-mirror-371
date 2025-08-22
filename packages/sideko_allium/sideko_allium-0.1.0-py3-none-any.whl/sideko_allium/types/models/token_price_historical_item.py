import pydantic


class TokenPriceHistoricalItem(pydantic.BaseModel):
    """
    TokenPriceHistoricalItem
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    close: float = pydantic.Field(
        alias="close",
    )
    high: float = pydantic.Field(
        alias="high",
    )
    low: float = pydantic.Field(
        alias="low",
    )
    open: float = pydantic.Field(
        alias="open",
    )
    price: float = pydantic.Field(
        alias="price",
    )
    timestamp: str = pydantic.Field(
        alias="timestamp",
    )
