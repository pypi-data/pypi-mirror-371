from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.wallet.balances import (
    AsyncBalancesClient,
    BalancesClient,
)
from sideko_allium.resources.developer.wallet.holdings import (
    AsyncHoldingsClient,
    HoldingsClient,
)
from sideko_allium.resources.developer.wallet.latest_nft_balances import (
    AsyncLatestNftBalancesClient,
    LatestNftBalancesClient,
)
from sideko_allium.resources.developer.wallet.latest_solana_nft_balances import (
    AsyncLatestSolanaNftBalancesClient,
    LatestSolanaNftBalancesClient,
)
from sideko_allium.resources.developer.wallet.nft_collections import (
    AsyncNftCollectionsClient,
    NftCollectionsClient,
)
from sideko_allium.resources.developer.wallet.pnl import AsyncPnlClient, PnlClient
from sideko_allium.resources.developer.wallet.pnl_by_token import (
    AsyncPnlByTokenClient,
    PnlByTokenClient,
)
from sideko_allium.resources.developer.wallet.transactions import (
    AsyncTransactionsClient,
    TransactionsClient,
)


class WalletClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.balances = BalancesClient(base_client=self._base_client)
        self.holdings = HoldingsClient(base_client=self._base_client)
        self.latest_nft_balances = LatestNftBalancesClient(
            base_client=self._base_client
        )
        self.latest_solana_nft_balances = LatestSolanaNftBalancesClient(
            base_client=self._base_client
        )
        self.nft_collections = NftCollectionsClient(base_client=self._base_client)
        self.pnl = PnlClient(base_client=self._base_client)
        self.pnl_by_token = PnlByTokenClient(base_client=self._base_client)
        self.transactions = TransactionsClient(base_client=self._base_client)


class AsyncWalletClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.balances = AsyncBalancesClient(base_client=self._base_client)
        self.holdings = AsyncHoldingsClient(base_client=self._base_client)
        self.latest_nft_balances = AsyncLatestNftBalancesClient(
            base_client=self._base_client
        )
        self.latest_solana_nft_balances = AsyncLatestSolanaNftBalancesClient(
            base_client=self._base_client
        )
        self.nft_collections = AsyncNftCollectionsClient(base_client=self._base_client)
        self.pnl = AsyncPnlClient(base_client=self._base_client)
        self.pnl_by_token = AsyncPnlByTokenClient(base_client=self._base_client)
        self.transactions = AsyncTransactionsClient(base_client=self._base_client)
