import pydantic
import typing

from .historical_pnl import HistoricalPnl


class ResponseEnvelopeHistoricalPnl_(pydantic.BaseModel):
    """
    ResponseEnvelopeHistoricalPnl_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    data: typing.Optional[HistoricalPnl] = pydantic.Field(alias="data", default=None)
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
    items: typing.Optional[typing.List[HistoricalPnl]] = pydantic.Field(
        alias="items", default=None
    )
