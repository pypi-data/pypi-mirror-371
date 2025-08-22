from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.bitcoin.mempool import (
    AsyncMempoolClient,
    MempoolClient,
)
from sideko_allium.resources.developer.bitcoin.ordinals import (
    AsyncOrdinalsClient,
    OrdinalsClient,
)
from sideko_allium.resources.developer.bitcoin.raw import AsyncRawClient, RawClient


class BitcoinClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.mempool = MempoolClient(base_client=self._base_client)
        self.ordinals = OrdinalsClient(base_client=self._base_client)
        self.raw = RawClient(base_client=self._base_client)


class AsyncBitcoinClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.mempool = AsyncMempoolClient(base_client=self._base_client)
        self.ordinals = AsyncOrdinalsClient(base_client=self._base_client)
        self.raw = AsyncRawClient(base_client=self._base_client)
