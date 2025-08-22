import pydantic
import typing

from .asset_amount import AssetAmount
from .solana_asset import SolanaAsset


class SolanaDexTradeActivity(pydantic.BaseModel):
    """
    SolanaDexTradeActivity
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
    asset_bought: SolanaAsset = pydantic.Field(
        alias="asset_bought",
    )
    asset_sold: SolanaAsset = pydantic.Field(
        alias="asset_sold",
    )
    log_index: typing.Optional[int] = pydantic.Field(
        alias="log_index",
    )
    project: typing.Optional[str] = pydantic.Field(
        alias="project",
    )
    protocol: typing.Optional[str] = pydantic.Field(
        alias="protocol",
    )
    type_: str = pydantic.Field(
        alias="type",
    )
