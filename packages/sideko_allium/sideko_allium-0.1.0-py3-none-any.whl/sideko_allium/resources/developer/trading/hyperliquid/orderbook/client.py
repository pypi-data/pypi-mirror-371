from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.trading.hyperliquid.orderbook.snapshot import (
    AsyncSnapshotClient,
    SnapshotClient,
)


class OrderbookClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.snapshot = SnapshotClient(base_client=self._base_client)


class AsyncOrderbookClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.snapshot = AsyncSnapshotClient(base_client=self._base_client)
