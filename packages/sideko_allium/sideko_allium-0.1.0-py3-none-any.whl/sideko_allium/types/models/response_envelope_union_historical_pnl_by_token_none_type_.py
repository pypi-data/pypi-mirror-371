import pydantic
import typing

from .historical_pnl_by_token import HistoricalPnlByToken


class ResponseEnvelopeUnionHistoricalPnlByTokenNoneType_(pydantic.BaseModel):
    """
    ResponseEnvelopeUnionHistoricalPnlByTokenNoneType_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    data: typing.Optional[HistoricalPnlByToken] = pydantic.Field(
        alias="data", default=None
    )
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
    items: typing.Optional[typing.List[typing.Optional[HistoricalPnlByToken]]] = (
        pydantic.Field(alias="items", default=None)
    )
