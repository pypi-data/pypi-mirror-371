import pydantic
import typing


class Trade(pydantic.BaseModel):
    """
    Trade
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    timestamp: str = pydantic.Field(
        alias="timestamp",
    )
    token_address: str = pydantic.Field(
        alias="token_address",
    )
    token_amount: float = pydantic.Field(
        alias="token_amount",
    )
    token_price_usd: typing.Optional[float] = pydantic.Field(
        alias="token_price_usd",
    )
