import pydantic
import typing
import typing_extensions

from .asset_amount import AssetAmount
from .evm_asset import EvmAsset


class EvmnftTradeActivity(pydantic.BaseModel):
    """
    EvmnftTradeActivity
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    asset: EvmAsset = pydantic.Field(
        alias="asset",
    )
    asset_amount: AssetAmount = pydantic.Field(
        alias="asset_amount",
    )
    buyer_address: str = pydantic.Field(
        alias="buyer_address",
    )
    creator_fee: typing.Optional[AssetAmount] = pydantic.Field(
        alias="creator_fee", default=None
    )
    creator_fee_receivers: typing.Optional[typing.List[str]] = pydantic.Field(
        alias="creator_fee_receivers", default=None
    )
    currency: EvmAsset = pydantic.Field(
        alias="currency",
    )
    currency_amount: AssetAmount = pydantic.Field(
        alias="currency_amount",
    )
    is_private: typing.Optional[bool] = pydantic.Field(alias="is_private", default=None)
    log_index: typing.Optional[int] = pydantic.Field(alias="log_index", default=None)
    marketplace: str = pydantic.Field(
        alias="marketplace",
    )
    platform_fee: typing.Optional[AssetAmount] = pydantic.Field(
        alias="platform_fee", default=None
    )
    platform_fee_receiver: typing.Optional[str] = pydantic.Field(
        alias="platform_fee_receiver", default=None
    )
    protocol: str = pydantic.Field(
        alias="protocol",
    )
    seller_address: str = pydantic.Field(
        alias="seller_address",
    )
    side: typing_extensions.Literal["buyer", "seller"] = pydantic.Field(
        alias="side",
    )
    trace_index: typing.Optional[int] = pydantic.Field(
        alias="trace_index", default=None
    )
    transaction_hash: str = pydantic.Field(
        alias="transaction_hash",
    )
    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
