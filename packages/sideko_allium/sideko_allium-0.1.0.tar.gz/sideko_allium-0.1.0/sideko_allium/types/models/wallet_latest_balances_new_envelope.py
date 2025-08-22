import pydantic
import typing

from .bitcoin_balances import BitcoinBalances
from .evm_wallet_balances import EvmWalletBalances
from .solana_balances import SolanaBalances
from .sui_wallet_latest_balances import SuiWalletLatestBalances


class WalletLatestBalancesNewEnvelope(pydantic.BaseModel):
    """
    WalletLatestBalancesNewEnvelope
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    items: typing.List[
        typing.Union[
            EvmWalletBalances, SolanaBalances, BitcoinBalances, SuiWalletLatestBalances
        ]
    ] = pydantic.Field(
        alias="items",
    )
