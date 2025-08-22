import pydantic

from .notional_amount import NotionalAmount


class TimeIntervalPnl(pydantic.BaseModel):
    """
    TimeIntervalPnl
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    realized_pnl: NotionalAmount = pydantic.Field(
        alias="realized_pnl",
    )
    timestamp: str = pydantic.Field(
        alias="timestamp",
    )
    unrealized_pnl: NotionalAmount = pydantic.Field(
        alias="unrealized_pnl",
    )
