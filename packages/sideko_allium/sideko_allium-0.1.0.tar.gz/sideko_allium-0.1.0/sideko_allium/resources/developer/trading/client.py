from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.trading.hyperliquid import (
    AsyncHyperliquidClient,
    HyperliquidClient,
)


class TradingClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.hyperliquid = HyperliquidClient(base_client=self._base_client)


class AsyncTradingClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.hyperliquid = AsyncHyperliquidClient(base_client=self._base_client)
