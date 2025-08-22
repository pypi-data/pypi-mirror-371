from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.state_prices.historical import (
    AsyncHistoricalClient,
    HistoricalClient,
)


class StatePricesClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.historical = HistoricalClient(base_client=self._base_client)


class AsyncStatePricesClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.historical = AsyncHistoricalClient(base_client=self._base_client)
