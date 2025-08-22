import pydantic
import typing

from .notional_amount import NotionalAmount
from .token_holding import TokenHolding


class AggregatedHoldings(pydantic.BaseModel):
    """
    AggregatedHoldings
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    amount: NotionalAmount = pydantic.Field(
        alias="amount",
    )
    timestamp: str = pydantic.Field(
        alias="timestamp",
    )
    token_breakdown: typing.Optional[typing.List[TokenHolding]] = pydantic.Field(
        alias="token_breakdown", default=None
    )
