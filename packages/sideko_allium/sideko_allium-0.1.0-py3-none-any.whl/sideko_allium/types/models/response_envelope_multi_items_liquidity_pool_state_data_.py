import pydantic
import typing

from .liquidity_pool_state_data import LiquidityPoolStateData


class ResponseEnvelopeMultiItemsLiquidityPoolStateData_(pydantic.BaseModel):
    """
    ResponseEnvelopeMultiItemsLiquidityPoolStateData_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
    items: typing.Optional[typing.List[LiquidityPoolStateData]] = pydantic.Field(
        alias="items", default=None
    )
