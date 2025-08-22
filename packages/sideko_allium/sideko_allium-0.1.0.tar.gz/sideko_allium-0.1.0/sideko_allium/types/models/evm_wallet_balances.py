import pydantic
import typing

from .token import Token


class EvmWalletBalances(pydantic.BaseModel):
    """
    EvmWalletBalances
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: str = pydantic.Field(
        alias="address",
    )
    block_hash: typing.Optional[str] = pydantic.Field(alias="block_hash", default=None)
    block_number: typing.Optional[int] = pydantic.Field(
        alias="block_number", default=None
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
