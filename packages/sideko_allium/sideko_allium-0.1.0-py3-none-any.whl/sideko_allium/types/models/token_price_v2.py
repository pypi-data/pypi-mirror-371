import pydantic
import typing

from .token_attributes import TokenAttributes


class TokenPriceV2(pydantic.BaseModel):
    """
    TokenPriceV2
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: str = pydantic.Field(
        alias="address",
    )
    attributes: TokenAttributes = pydantic.Field(
        alias="attributes",
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
