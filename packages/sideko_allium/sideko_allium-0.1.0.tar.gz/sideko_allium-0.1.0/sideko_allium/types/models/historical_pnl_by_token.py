import pydantic
import typing

from .time_interval_pnl import TimeIntervalPnl


class HistoricalPnlByToken(pydantic.BaseModel):
    """
    HistoricalPnlByToken
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: str = pydantic.Field(
        alias="address",
    )
    chain: str = pydantic.Field(
        alias="chain",
    )
    pnl: typing.List[TimeIntervalPnl] = pydantic.Field(
        alias="pnl",
    )
    token_address: typing.Optional[str] = pydantic.Field(
        alias="token_address", default=None
    )
