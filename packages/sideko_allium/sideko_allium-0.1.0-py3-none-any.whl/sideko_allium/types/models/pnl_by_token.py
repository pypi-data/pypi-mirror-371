import pydantic
import typing

from .notional_amount import NotionalAmount
from .pnl_data_per_transaction import PnlDataPerTransaction


class PnlByToken(pydantic.BaseModel):
    """
    PnlByToken
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: str = pydantic.Field(
        alias="address",
    )
    average_cost: typing.Optional[NotionalAmount] = pydantic.Field(
        alias="average_cost", default=None
    )
    chain: str = pydantic.Field(
        alias="chain",
    )
    current_balance: NotionalAmount = pydantic.Field(
        alias="current_balance",
    )
    current_price: NotionalAmount = pydantic.Field(
        alias="current_price",
    )
    current_tokens: float = pydantic.Field(
        alias="current_tokens",
    )
    historical_breakdown: typing.Optional[typing.List[PnlDataPerTransaction]] = (
        pydantic.Field(alias="historical_breakdown", default=None)
    )
    realized_pnl: typing.Optional[NotionalAmount] = pydantic.Field(
        alias="realized_pnl", default=None
    )
    token_address: str = pydantic.Field(
        alias="token_address",
    )
    unrealized_pnl: typing.Optional[NotionalAmount] = pydantic.Field(
        alias="unrealized_pnl", default=None
    )
    unrealized_pnl_ratio_change: typing.Optional[float] = pydantic.Field(
        alias="unrealized_pnl_ratio_change", default=None
    )
