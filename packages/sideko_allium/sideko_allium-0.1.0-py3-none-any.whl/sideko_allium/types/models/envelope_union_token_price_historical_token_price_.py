import pydantic
import typing

from .token_price import TokenPrice
from .token_price_historical import TokenPriceHistorical


class EnvelopeUnionTokenPriceHistoricalTokenPrice_(pydantic.BaseModel):
    """
    EnvelopeUnionTokenPriceHistoricalTokenPrice_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    items: typing.List[typing.Union[TokenPriceHistorical, TokenPrice]] = pydantic.Field(
        alias="items",
    )
