import pydantic
import typing

from .asset_amount import AssetAmount
from .solana_asset_transfer import SolanaAssetTransfer
from .solana_dex_trade_activity import SolanaDexTradeActivity
from .solana_nft_trade_activity import SolanaNftTradeActivity


class SolanaWalletTransaction(pydantic.BaseModel):
    """
    SolanaWalletTransaction
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    activities: typing.List[
        typing.Union[SolanaNftTradeActivity, SolanaDexTradeActivity]
    ] = pydantic.Field(
        alias="activities",
    )
    address: str = pydantic.Field(
        alias="address",
    )
    asset_transfers: typing.List[SolanaAssetTransfer] = pydantic.Field(
        alias="asset_transfers",
    )
    block_hash: typing.Optional[str] = pydantic.Field(
        alias="block_hash",
    )
    block_number: int = pydantic.Field(
        alias="block_number",
    )
    block_timestamp: str = pydantic.Field(
        alias="block_timestamp",
    )
    chain: str = pydantic.Field(
        alias="chain",
    )
    fee: AssetAmount = pydantic.Field(
        alias="fee",
    )
    from_address: typing.Optional[str] = pydantic.Field(
        alias="from_address",
    )
    hash: str = pydantic.Field(
        alias="hash",
    )
    id: str = pydantic.Field(
        alias="id",
    )
    index: int = pydantic.Field(
        alias="index",
    )
    labels: typing.List[str] = pydantic.Field(
        alias="labels",
    )
    to_address: typing.Optional[str] = pydantic.Field(
        alias="to_address",
    )
    within_block_order_key: int = pydantic.Field(
        alias="within_block_order_key",
    )
