from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.wallet.holdings.history import (
    AsyncHistoryClient,
    HistoryClient,
)


class HoldingsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.history = HistoryClient(base_client=self._base_client)


class AsyncHoldingsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.history = AsyncHistoryClient(base_client=self._base_client)
