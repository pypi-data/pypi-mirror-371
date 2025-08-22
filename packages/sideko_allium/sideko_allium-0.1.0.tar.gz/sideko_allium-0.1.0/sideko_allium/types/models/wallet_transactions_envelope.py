import pydantic
import typing

from .bitcoin_wallet_transaction import BitcoinWalletTransaction
from .evm_wallet_transaction import EvmWalletTransaction
from .solana_wallet_transaction import SolanaWalletTransaction


class WalletTransactionsEnvelope(pydantic.BaseModel):
    """
    WalletTransactionsEnvelope
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    items: typing.List[
        typing.Union[
            EvmWalletTransaction, SolanaWalletTransaction, BitcoinWalletTransaction
        ]
    ] = pydantic.Field(
        alias="items",
    )
