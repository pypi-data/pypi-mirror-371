import pydantic
import typing


class TokenAttributes(pydantic.BaseModel):
    """
    TokenAttributes
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    price_diff_1d: typing.Optional[float] = pydantic.Field(
        alias="price_diff_1d", default=None
    )
    price_diff_pct_1d: typing.Optional[float] = pydantic.Field(
        alias="price_diff_pct_1d", default=None
    )
    total_liquidity_usd: typing.Optional[typing.Union[float, str]] = pydantic.Field(
        alias="total_liquidity_usd", default=None
    )
    total_market_cap_usd: typing.Optional[float] = pydantic.Field(
        alias="total_market_cap_usd", default=None
    )
    total_supply: typing.Optional[float] = pydantic.Field(
        alias="total_supply", default=None
    )
    volume_1h: typing.Optional[float] = pydantic.Field(alias="volume_1h", default=None)
    volume_24h: typing.Optional[float] = pydantic.Field(
        alias="volume_24h", default=None
    )
    volume_usd_1h: typing.Optional[float] = pydantic.Field(
        alias="volume_usd_1h", default=None
    )
    volume_usd_24h: typing.Optional[float] = pydantic.Field(
        alias="volume_usd_24h", default=None
    )
