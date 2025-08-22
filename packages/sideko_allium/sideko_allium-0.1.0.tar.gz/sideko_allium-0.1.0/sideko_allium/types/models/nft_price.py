import pydantic

from .asset_amount import AssetAmount
from .base_asset_detail import BaseAssetDetail


class NftPrice(pydantic.BaseModel):
    """
    NftPrice
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    amount: AssetAmount = pydantic.Field(
        alias="amount",
    )
    asset: BaseAssetDetail = pydantic.Field(
        alias="asset",
    )
