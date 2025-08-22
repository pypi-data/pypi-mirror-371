from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.dex.trades import AsyncTradesClient, TradesClient


class DexClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.trades = TradesClient(base_client=self._base_client)


class AsyncDexClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.trades = AsyncTradesClient(base_client=self._base_client)
