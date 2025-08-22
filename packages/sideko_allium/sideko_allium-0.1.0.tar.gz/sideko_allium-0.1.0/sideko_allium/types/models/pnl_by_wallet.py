import pydantic
import typing

from .notional_amount import NotionalAmount
from .pnl_by_wallet_average_cost import PnlByWalletAverageCost
from .pnl_by_wallet_current_balances import PnlByWalletCurrentBalances
from .pnl_by_wallet_current_prices import PnlByWalletCurrentPrices
from .pnl_by_wallet_current_tokens import PnlByWalletCurrentTokens
from .pnl_by_wallet_realized_pnl import PnlByWalletRealizedPnl
from .pnl_by_wallet_unrealized_pnl import PnlByWalletUnrealizedPnl
from .pnl_by_wallet_unrealized_pnl_ratio_change import (
    PnlByWalletUnrealizedPnlRatioChange,
)
from .pnl_data_per_transaction import PnlDataPerTransaction


class PnlByWallet(pydantic.BaseModel):
    """
    PnlByWallet
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: str = pydantic.Field(
        alias="address",
    )
    average_cost: PnlByWalletAverageCost = pydantic.Field(
        alias="average_cost",
    )
    chain: str = pydantic.Field(
        alias="chain",
    )
    current_balances: PnlByWalletCurrentBalances = pydantic.Field(
        alias="current_balances",
    )
    current_prices: PnlByWalletCurrentPrices = pydantic.Field(
        alias="current_prices",
    )
    current_tokens: PnlByWalletCurrentTokens = pydantic.Field(
        alias="current_tokens",
    )
    historical_breakdown: typing.Optional[typing.List[PnlDataPerTransaction]] = (
        pydantic.Field(alias="historical_breakdown", default=None)
    )
    realized_pnl: PnlByWalletRealizedPnl = pydantic.Field(
        alias="realized_pnl",
    )
    total_balance: NotionalAmount = pydantic.Field(
        alias="total_balance",
    )
    total_realized_pnl: NotionalAmount = pydantic.Field(
        alias="total_realized_pnl",
    )
    total_unrealized_pnl: NotionalAmount = pydantic.Field(
        alias="total_unrealized_pnl",
    )
    total_unrealized_pnl_ratio_change: typing.Optional[float] = pydantic.Field(
        alias="total_unrealized_pnl_ratio_change",
    )
    unrealized_pnl: PnlByWalletUnrealizedPnl = pydantic.Field(
        alias="unrealized_pnl",
    )
    unrealized_pnl_ratio_change: PnlByWalletUnrealizedPnlRatioChange = pydantic.Field(
        alias="unrealized_pnl_ratio_change",
    )
