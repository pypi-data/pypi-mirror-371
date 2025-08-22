import pydantic
import typing

from .bitcoin_balances import BitcoinBalances
from .evm_wallet_balances import EvmWalletBalances
from .legacy_evm_wallet_balances import LegacyEvmWalletBalances
from .legacy_solana_balances import LegacySolanaBalances
from .solana_balances import SolanaBalances


class ApiServerAppServicesWalletBalancesWalletHistoricalBalancesClientEnvelope(
    pydantic.BaseModel
):
    """
    ApiServerAppServicesWalletBalancesWalletHistoricalBalancesClientEnvelope
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    items: typing.List[
        typing.Union[
            SolanaBalances,
            BitcoinBalances,
            EvmWalletBalances,
            LegacyEvmWalletBalances,
            LegacySolanaBalances,
        ]
    ] = pydantic.Field(
        alias="items",
    )
