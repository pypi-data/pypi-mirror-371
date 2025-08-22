import pydantic
import typing


class ProtocolSpecificFields(pydantic.BaseModel):
    """
    ProtocolSpecificFields
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    liquidity_delta: typing.Optional[str] = pydantic.Field(
        alias="liquidity_delta", default=None
    )
    sqrt_price_x96: typing.Optional[str] = pydantic.Field(
        alias="sqrt_price_x96", default=None
    )
    tick_lower: typing.Optional[int] = pydantic.Field(alias="tick_lower", default=None)
    tick_upper: typing.Optional[int] = pydantic.Field(alias="tick_upper", default=None)
