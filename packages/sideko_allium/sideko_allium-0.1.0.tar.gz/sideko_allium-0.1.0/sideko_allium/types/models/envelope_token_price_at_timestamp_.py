import pydantic
import typing

from .token_price_at_timestamp import TokenPriceAtTimestamp


class EnvelopeTokenPriceAtTimestamp_(pydantic.BaseModel):
    """
    EnvelopeTokenPriceAtTimestamp_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    items: typing.List[TokenPriceAtTimestamp] = pydantic.Field(
        alias="items",
    )
