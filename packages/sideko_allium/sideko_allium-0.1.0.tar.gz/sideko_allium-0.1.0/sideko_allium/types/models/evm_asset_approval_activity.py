import pydantic
import typing
import typing_extensions

from .asset_amount import AssetAmount
from .evm_asset import EvmAsset


class EvmAssetApprovalActivity(pydantic.BaseModel):
    """
    EvmAssetApprovalActivity
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    approved_amount: typing.Optional[AssetAmount] = pydantic.Field(
        alias="approved_amount",
    )
    asset: EvmAsset = pydantic.Field(
        alias="asset",
    )
    contract_address: typing.Optional[str] = pydantic.Field(
        alias="contract_address",
    )
    granularity: typing_extensions.Literal["collection", "token"] = pydantic.Field(
        alias="granularity",
    )
    log_index: typing.Optional[int] = pydantic.Field(alias="log_index", default=None)
    spender_address: typing.Optional[str] = pydantic.Field(
        alias="spender_address",
    )
    status: typing_extensions.Literal["approved", "revoked"] = pydantic.Field(
        alias="status",
    )
    trace_index: typing.Optional[int] = pydantic.Field(
        alias="trace_index", default=None
    )
    transaction_hash: str = pydantic.Field(
        alias="transaction_hash",
    )
    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
