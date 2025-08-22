import pydantic


class TokenBalance(pydantic.BaseModel):
    """
    TokenBalance
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    account: str = pydantic.Field(
        alias="account",
    )
    account_index: int = pydantic.Field(
        alias="account_index",
    )
    amount: str = pydantic.Field(
        alias="amount",
    )
    decimals: int = pydantic.Field(
        alias="decimals",
    )
    mint: str = pydantic.Field(
        alias="mint",
    )
    owner: str = pydantic.Field(
        alias="owner",
    )
