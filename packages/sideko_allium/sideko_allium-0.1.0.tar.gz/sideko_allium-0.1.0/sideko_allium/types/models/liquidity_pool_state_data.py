import pydantic
import typing


class LiquidityPoolStateData(pydantic.BaseModel):
    """
    Model for liquidity pool state data.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    base_symbol: str = pydantic.Field(
        alias="base_symbol",
    )
    """
    Base token symbol
    """
    block_number: int = pydantic.Field(
        alias="block_number",
    )
    """
    Block number
    """
    block_timestamp: str = pydantic.Field(
        alias="block_timestamp",
    )
    """
    Block timestamp
    """
    blockchain: str = pydantic.Field(
        alias="blockchain",
    )
    """
    The blockchain name
    """
    market_depth_minus_1_percent_quote: float = pydantic.Field(
        alias="market_depth_minus_1_percent_quote",
    )
    """
    -1% market depth (amount of quote token)
    """
    market_depth_minus_1_percent_usd: typing.Optional[float] = pydantic.Field(
        alias="market_depth_minus_1_percent_usd", default=None
    )
    market_depth_plus_1_percent_base: float = pydantic.Field(
        alias="market_depth_plus_1_percent_base",
    )
    """
    +1% market depth (amount of base token)
    """
    market_depth_plus_1_percent_usd: typing.Optional[float] = pydantic.Field(
        alias="market_depth_plus_1_percent_usd", default=None
    )
    pool_address: str = pydantic.Field(
        alias="pool_address",
    )
    """
    Pool contract address
    """
    pool_id: typing.Optional[str] = pydantic.Field(
        alias="pool_id",
    )
    pool_weight: float = pydantic.Field(
        alias="pool_weight",
    )
    """
    Pool weight
    """
    quote_address: typing.Optional[str] = pydantic.Field(
        alias="quote_address", default=None
    )
    quote_price_usd: typing.Optional[float] = pydantic.Field(
        alias="quote_price_usd", default=None
    )
    quote_symbol: str = pydantic.Field(
        alias="quote_symbol",
    )
    """
    Quote token symbol
    """
    state_price: float = pydantic.Field(
        alias="state_price",
    )
    """
    Current state price
    """
    state_price_usd: typing.Optional[float] = pydantic.Field(
        alias="state_price_usd", default=None
    )
    usd_trading_volume_current_block: typing.Optional[float] = pydantic.Field(
        alias="usd_trading_volume_current_block", default=None
    )
