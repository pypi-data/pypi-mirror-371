import pydantic
import typing
import typing_extensions

from .asset_amount import AssetAmount
from .evm_asset import EvmAsset


class EvmTransfer(pydantic.BaseModel):
    """
    EvmTransfer
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    amount: AssetAmount = pydantic.Field(
        alias="amount",
    )
    asset: EvmAsset = pydantic.Field(
        alias="asset",
    )
    from_address: str = pydantic.Field(
        alias="from_address",
    )
    log_index: typing.Optional[int] = pydantic.Field(alias="log_index", default=None)
    to_address: str = pydantic.Field(
        alias="to_address",
    )
    transaction_hash: str = pydantic.Field(
        alias="transaction_hash",
    )
    transfer_type: typing_extensions.Literal["burned", "minted", "received", "sent"] = (
        pydantic.Field(
            alias="transfer_type",
        )
    )
