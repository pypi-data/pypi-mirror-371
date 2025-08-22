import pydantic

from .token import Token


class SuiWalletLatestBalances(pydantic.BaseModel):
    """
    SuiWalletLatestBalances
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: str = pydantic.Field(
        alias="address",
    )
    block_timestamp: str = pydantic.Field(
        alias="block_timestamp",
    )
    chain: str = pydantic.Field(
        alias="chain",
    )
    raw_balance: int = pydantic.Field(
        alias="raw_balance",
    )
    token: Token = pydantic.Field(
        alias="token",
    )
