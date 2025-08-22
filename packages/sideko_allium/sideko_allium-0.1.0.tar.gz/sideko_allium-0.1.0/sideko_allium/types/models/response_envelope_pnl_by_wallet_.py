import pydantic
import typing

from .pnl_by_wallet import PnlByWallet


class ResponseEnvelopePnlByWallet_(pydantic.BaseModel):
    """
    ResponseEnvelopePnlByWallet_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    data: typing.Optional[PnlByWallet] = pydantic.Field(alias="data", default=None)
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
    items: typing.Optional[typing.List[PnlByWallet]] = pydantic.Field(
        alias="items", default=None
    )
