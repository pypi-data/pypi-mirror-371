from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.bitcoin import AsyncBitcoinClient, BitcoinClient
from sideko_allium.resources.developer.dex import AsyncDexClient, DexClient
from sideko_allium.resources.developer.nfts import AsyncNftsClient, NftsClient
from sideko_allium.resources.developer.prices import AsyncPricesClient, PricesClient
from sideko_allium.resources.developer.raw import AsyncRawClient, RawClient
from sideko_allium.resources.developer.solana import AsyncSolanaClient, SolanaClient
from sideko_allium.resources.developer.sql import AsyncSqlClient, SqlClient
from sideko_allium.resources.developer.state_prices import (
    AsyncStatePricesClient,
    StatePricesClient,
)
from sideko_allium.resources.developer.tokens import AsyncTokensClient, TokensClient
from sideko_allium.resources.developer.trading import AsyncTradingClient, TradingClient
from sideko_allium.resources.developer.wallet import AsyncWalletClient, WalletClient


class DeveloperClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.bitcoin = BitcoinClient(base_client=self._base_client)
        self.nfts = NftsClient(base_client=self._base_client)
        self.solana = SolanaClient(base_client=self._base_client)
        self.trading = TradingClient(base_client=self._base_client)
        self.dex = DexClient(base_client=self._base_client)
        self.raw = RawClient(base_client=self._base_client)
        self.prices = PricesClient(base_client=self._base_client)
        self.state_prices = StatePricesClient(base_client=self._base_client)
        self.tokens = TokensClient(base_client=self._base_client)
        self.wallet = WalletClient(base_client=self._base_client)
        self.sql = SqlClient(base_client=self._base_client)


class AsyncDeveloperClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.bitcoin = AsyncBitcoinClient(base_client=self._base_client)
        self.nfts = AsyncNftsClient(base_client=self._base_client)
        self.solana = AsyncSolanaClient(base_client=self._base_client)
        self.trading = AsyncTradingClient(base_client=self._base_client)
        self.dex = AsyncDexClient(base_client=self._base_client)
        self.raw = AsyncRawClient(base_client=self._base_client)
        self.prices = AsyncPricesClient(base_client=self._base_client)
        self.state_prices = AsyncStatePricesClient(base_client=self._base_client)
        self.tokens = AsyncTokensClient(base_client=self._base_client)
        self.wallet = AsyncWalletClient(base_client=self._base_client)
        self.sql = AsyncSqlClient(base_client=self._base_client)
