import pydantic
import typing

from .asset_amount import AssetAmount
from .bitcoin_asset_transfer import BitcoinAssetTransfer


class BitcoinWalletTransaction(pydantic.BaseModel):
    """
    BitcoinWalletTransaction
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    activities: typing.List[typing.Any] = pydantic.Field(
        alias="activities",
    )
    address: str = pydantic.Field(
        alias="address",
    )
    asset_transfers: typing.List[BitcoinAssetTransfer] = pydantic.Field(
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
    within_block_order_key: int = pydantic.Field(
        alias="within_block_order_key",
    )
