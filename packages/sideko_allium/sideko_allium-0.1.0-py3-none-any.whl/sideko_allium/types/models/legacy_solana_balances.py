import pydantic
import typing

from .token_metadata import TokenMetadata
from .token_metadata_with_price_info import TokenMetadataWithPriceInfo


class LegacySolanaBalances(pydantic.BaseModel):
    """
    LegacySolanaBalances
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
    decimals: int = pydantic.Field(
        alias="decimals",
    )
    mint: str = pydantic.Field(
        alias="mint",
    )
    raw_balance: int = pydantic.Field(
        alias="raw_balance",
    )
    token_account: typing.Optional[str] = pydantic.Field(
        alias="token_account",
    )
    token_metadata: typing.Optional[
        typing.Union[TokenMetadataWithPriceInfo, TokenMetadata]
    ] = pydantic.Field(alias="token_metadata", default=None)
    txn_id: str = pydantic.Field(
        alias="txn_id",
    )
    txn_index: int = pydantic.Field(
        alias="txn_index",
    )
