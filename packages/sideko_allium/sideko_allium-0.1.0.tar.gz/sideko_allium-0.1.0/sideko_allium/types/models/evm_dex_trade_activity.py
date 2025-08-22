import pydantic
import typing

from .asset_amount import AssetAmount
from .evm_asset import EvmAsset


class EvmDexTradeActivity(pydantic.BaseModel):
    """
    EvmDexTradeActivity
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    amount_bought: AssetAmount = pydantic.Field(
        alias="amount_bought",
    )
    amount_sold: AssetAmount = pydantic.Field(
        alias="amount_sold",
    )
    asset_bought: EvmAsset = pydantic.Field(
        alias="asset_bought",
    )
    asset_sold: EvmAsset = pydantic.Field(
        alias="asset_sold",
    )
    log_index: typing.Optional[int] = pydantic.Field(alias="log_index", default=None)
    project: typing.Optional[str] = pydantic.Field(
        alias="project",
    )
    protocol: typing.Optional[str] = pydantic.Field(
        alias="protocol",
    )
    trace_index: typing.Optional[int] = pydantic.Field(
        alias="trace_index", default=None
    )
    transaction_hash: str = pydantic.Field(
        alias="transaction_hash",
    )
    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
