import pydantic
import typing

from .notional_amount import NotionalAmount


class PnlByWalletUnrealizedPnl(pydantic.BaseModel):
    """
    PnlByWalletUnrealizedPnl
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Optional[NotionalAmount]]
