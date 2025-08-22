import pydantic
import typing

from .asset_amount import AssetAmount
from .evm_asset import EvmAsset


class EvmAssetBridgeActivity(pydantic.BaseModel):
    """
    EvmAssetBridgeActivity
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    destination_chain: str = pydantic.Field(
        alias="destination_chain",
    )
    direction: str = pydantic.Field(
        alias="direction",
    )
    log_index: typing.Optional[int] = pydantic.Field(alias="log_index", default=None)
    protocol: str = pydantic.Field(
        alias="protocol",
    )
    recipient_address: str = pydantic.Field(
        alias="recipient_address",
    )
    sender_address: str = pydantic.Field(
        alias="sender_address",
    )
    source_chain: str = pydantic.Field(
        alias="source_chain",
    )
    token_in_amount: AssetAmount = pydantic.Field(
        alias="token_in_amount",
    )
    token_in_asset: EvmAsset = pydantic.Field(
        alias="token_in_asset",
    )
    token_out_amount: AssetAmount = pydantic.Field(
        alias="token_out_amount",
    )
    token_out_asset: EvmAsset = pydantic.Field(
        alias="token_out_asset",
    )
    trace_index: typing.Optional[int] = pydantic.Field(
        alias="trace_index", default=None
    )
    transaction_hash: str = pydantic.Field(
        alias="transaction_hash",
    )
    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
