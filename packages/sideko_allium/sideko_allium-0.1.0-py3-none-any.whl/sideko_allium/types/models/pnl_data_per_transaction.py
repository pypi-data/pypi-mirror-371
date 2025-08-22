import pydantic
import typing

from .notional_amount import NotionalAmount
from .trade import Trade


class PnlDataPerTransaction(pydantic.BaseModel):
    """
    PnlDataPerTransaction
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    average_cost: typing.Optional[NotionalAmount] = pydantic.Field(
        alias="average_cost",
    )
    realized_pnl: NotionalAmount = pydantic.Field(
        alias="realized_pnl",
    )
    trade: Trade = pydantic.Field(
        alias="trade",
    )
