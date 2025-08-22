import pydantic
import typing

from .pnl_by_token import PnlByToken


class ResponseEnvelopeUnionPnlByTokenNoneType_(pydantic.BaseModel):
    """
    ResponseEnvelopeUnionPnlByTokenNoneType_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    data: typing.Optional[PnlByToken] = pydantic.Field(alias="data", default=None)
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
    items: typing.Optional[typing.List[typing.Optional[PnlByToken]]] = pydantic.Field(
        alias="items", default=None
    )
