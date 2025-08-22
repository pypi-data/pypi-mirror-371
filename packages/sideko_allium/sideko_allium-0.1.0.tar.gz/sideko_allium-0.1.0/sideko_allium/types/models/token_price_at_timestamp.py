import pydantic


class TokenPriceAtTimestamp(pydantic.BaseModel):
    """
    TokenPriceAtTimestamp
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    chain: str = pydantic.Field(
        alias="chain",
    )
    input_timestamp: str = pydantic.Field(
        alias="input_timestamp",
    )
    mint: str = pydantic.Field(
        alias="mint",
    )
    price: float = pydantic.Field(
        alias="price",
    )
    price_timestamp: str = pydantic.Field(
        alias="price_timestamp",
    )
