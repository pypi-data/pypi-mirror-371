import pydantic
import typing

from .token_price_historical_item import TokenPriceHistoricalItem


class TokenPriceHistorical(pydantic.BaseModel):
    """
    TokenPriceHistorical
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    chain: str = pydantic.Field(
        alias="chain",
    )
    decimals: int = pydantic.Field(
        alias="decimals",
    )
    mint: str = pydantic.Field(
        alias="mint",
    )
    prices: typing.List[TokenPriceHistoricalItem] = pydantic.Field(
        alias="prices",
    )
