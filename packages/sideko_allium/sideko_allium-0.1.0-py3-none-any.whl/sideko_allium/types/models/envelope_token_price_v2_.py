import pydantic
import typing

from .token_price_v2 import TokenPriceV2


class EnvelopeTokenPriceV2_(pydantic.BaseModel):
    """
    EnvelopeTokenPriceV2_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    items: typing.List[TokenPriceV2] = pydantic.Field(
        alias="items",
    )
