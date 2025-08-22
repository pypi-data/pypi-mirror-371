import pydantic
import typing
import typing_extensions

from .asset_amount import AssetAmount
from .brc20_asset_detail import Brc20AssetDetail
from .native_asset_detail import NativeAssetDetail
from .ordinal_inscription_asset_detail import OrdinalInscriptionAssetDetail


class BitcoinAssetTransfer(pydantic.BaseModel):
    """
    AssetTransfer to represent the asset transfer.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    amount: AssetAmount = pydantic.Field(
        alias="amount",
    )
    asset: typing.Union[
        NativeAssetDetail, Brc20AssetDetail, OrdinalInscriptionAssetDetail
    ] = pydantic.Field(
        alias="asset",
    )
    from_address: typing.Optional[str] = pydantic.Field(
        alias="from_address", default=None
    )
    to_address: typing.Optional[str] = pydantic.Field(alias="to_address", default=None)
    transfer_type: typing_extensions.Literal["received", "sent"] = pydantic.Field(
        alias="transfer_type",
    )
