import pydantic
import typing


class TokenPrice(pydantic.BaseModel):
    """
    TokenPrice
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    chain: str = pydantic.Field(
        alias="chain",
    )
    close: float = pydantic.Field(
        alias="close",
    )
    decimals: typing.Optional[int] = pydantic.Field(alias="decimals", default=None)
    high: float = pydantic.Field(
        alias="high",
    )
    low: float = pydantic.Field(
        alias="low",
    )
    mint: str = pydantic.Field(
        alias="mint",
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
    trade_count_1h: typing.Optional[int] = pydantic.Field(
        alias="trade_count_1h", default=None
    )
    trade_count_24h: typing.Optional[int] = pydantic.Field(
        alias="trade_count_24h", default=None
    )
    volume_1h: typing.Optional[float] = pydantic.Field(alias="volume_1h", default=None)
    volume_24h: typing.Optional[float] = pydantic.Field(
        alias="volume_24h", default=None
    )
