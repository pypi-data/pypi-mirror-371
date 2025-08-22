import pydantic
import typing
import typing_extensions

from .asset_amount import AssetAmount
from .solana_asset import SolanaAsset


class SolanaNftTradeActivity(pydantic.BaseModel):
    """
    SolanaNftTradeActivity
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    asset: SolanaAsset = pydantic.Field(
        alias="asset",
    )
    asset_amount: AssetAmount = pydantic.Field(
        alias="asset_amount",
    )
    currency: SolanaAsset = pydantic.Field(
        alias="currency",
    )
    currency_amount: AssetAmount = pydantic.Field(
        alias="currency_amount",
    )
    marketplace: typing.Optional[str] = pydantic.Field(
        alias="marketplace",
    )
    protocol: typing.Optional[str] = pydantic.Field(
        alias="protocol",
    )
    side: typing_extensions.Literal["buyer", "seller"] = pydantic.Field(
        alias="side",
    )
    type_: str = pydantic.Field(
        alias="type",
    )
