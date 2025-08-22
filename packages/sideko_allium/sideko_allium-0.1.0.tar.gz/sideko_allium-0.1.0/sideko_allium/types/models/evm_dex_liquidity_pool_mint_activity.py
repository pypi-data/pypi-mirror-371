import pydantic
import typing

from .asset_amount import AssetAmount
from .evm_asset import EvmAsset
from .protocol_specific_fields import ProtocolSpecificFields


class EvmDexLiquidityPoolMintActivity(pydantic.BaseModel):
    """
    EvmDexLiquidityPoolMintActivity
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    liquidity_pool_address: str = pydantic.Field(
        alias="liquidity_pool_address",
    )
    log_index: int = pydantic.Field(
        alias="log_index",
    )
    lp_tokens_amount: typing.Optional[int] = pydantic.Field(
        alias="lp_tokens_amount", default=None
    )
    project: typing.Optional[str] = pydantic.Field(alias="project", default=None)
    protocol: typing.Optional[str] = pydantic.Field(alias="protocol", default=None)
    protocol_specific_fields: typing.Optional[ProtocolSpecificFields] = pydantic.Field(
        alias="protocol_specific_fields", default=None
    )
    token0: EvmAsset = pydantic.Field(
        alias="token0",
    )
    token0_amount: AssetAmount = pydantic.Field(
        alias="token0_amount",
    )
    token1: EvmAsset = pydantic.Field(
        alias="token1",
    )
    token1_amount: AssetAmount = pydantic.Field(
        alias="token1_amount",
    )
    transaction_hash: str = pydantic.Field(
        alias="transaction_hash",
    )
    type_: str = pydantic.Field(
        alias="type",
    )
