import pydantic
import typing
import typing_extensions

from .asset_amount import AssetAmount
from .solana_asset import SolanaAsset


class SolanaAssetTransfer(pydantic.BaseModel):
    """
    SolanaAssetTransfer
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    amount: AssetAmount = pydantic.Field(
        alias="amount",
    )
    asset: SolanaAsset = pydantic.Field(
        alias="asset",
    )
    from_address: typing.Optional[str] = pydantic.Field(
        alias="from_address", default=None
    )
    from_token_account: typing.Optional[str] = pydantic.Field(
        alias="from_token_account", default=None
    )
    log_index: typing.Optional[int] = pydantic.Field(alias="log_index", default=None)
    to_address: typing.Optional[str] = pydantic.Field(alias="to_address", default=None)
    to_token_account: typing.Optional[str] = pydantic.Field(
        alias="to_token_account", default=None
    )
    transaction_hash: typing.Optional[str] = pydantic.Field(
        alias="transaction_hash", default=None
    )
    transfer_type: typing_extensions.Literal[
        "burned", "invalid", "minted", "received", "sent"
    ] = pydantic.Field(
        alias="transfer_type",
    )
