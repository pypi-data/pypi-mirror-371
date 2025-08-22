from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.trading.hyperliquid.info import (
    AsyncInfoClient,
    InfoClient,
)
from sideko_allium.resources.developer.trading.hyperliquid.orderbook import (
    AsyncOrderbookClient,
    OrderbookClient,
)


class HyperliquidClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.orderbook = OrderbookClient(base_client=self._base_client)
        self.info = InfoClient(base_client=self._base_client)


class AsyncHyperliquidClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.orderbook = AsyncOrderbookClient(base_client=self._base_client)
        self.info = AsyncInfoClient(base_client=self._base_client)
