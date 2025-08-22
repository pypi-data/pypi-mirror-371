import pydantic
import typing

from .token import Token


class SolanaBalances(pydantic.BaseModel):
    """
    SolanaBalances
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: str = pydantic.Field(
        alias="address",
    )
    block_hash: str = pydantic.Field(
        alias="block_hash",
    )
    block_slot: int = pydantic.Field(
        alias="block_slot",
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
    token_account: typing.Optional[str] = pydantic.Field(
        alias="token_account",
    )
    txn_id: str = pydantic.Field(
        alias="txn_id",
    )
    txn_index: int = pydantic.Field(
        alias="txn_index",
    )
