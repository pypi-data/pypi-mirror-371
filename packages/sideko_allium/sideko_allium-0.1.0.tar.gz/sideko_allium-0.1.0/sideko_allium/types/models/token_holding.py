import pydantic

from .notional_amount import NotionalAmount


class TokenHolding(pydantic.BaseModel):
    """
    TokenHolding
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    amount: NotionalAmount = pydantic.Field(
        alias="amount",
    )
    chain: str = pydantic.Field(
        alias="chain",
    )
    token_address: str = pydantic.Field(
        alias="token_address",
    )
