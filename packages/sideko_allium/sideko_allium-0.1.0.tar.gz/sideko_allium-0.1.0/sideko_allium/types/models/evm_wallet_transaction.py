import pydantic
import typing

from .asset_amount import AssetAmount
from .evm_asset_approval_activity import EvmAssetApprovalActivity
from .evm_asset_bridge_activity import EvmAssetBridgeActivity
from .evm_dex_liquidity_pool_burn_activity import EvmDexLiquidityPoolBurnActivity
from .evm_dex_liquidity_pool_mint_activity import EvmDexLiquidityPoolMintActivity
from .evm_dex_trade_activity import EvmDexTradeActivity
from .evm_transfer import EvmTransfer
from .evmnft_trade_activity import EvmnftTradeActivity


class EvmWalletTransaction(pydantic.BaseModel):
    """
    EvmWalletTransaction
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    activities: typing.List[
        typing.Union[
            EvmAssetApprovalActivity,
            EvmnftTradeActivity,
            EvmDexTradeActivity,
            EvmAssetBridgeActivity,
            EvmDexLiquidityPoolBurnActivity,
            EvmDexLiquidityPoolMintActivity,
        ]
    ] = pydantic.Field(
        alias="activities",
    )
    address: str = pydantic.Field(
        alias="address",
    )
    asset_transfers: typing.List[EvmTransfer] = pydantic.Field(
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
    type_: typing.Optional[int] = pydantic.Field(
        alias="type",
    )
    within_block_order_key: int = pydantic.Field(
        alias="within_block_order_key",
    )
