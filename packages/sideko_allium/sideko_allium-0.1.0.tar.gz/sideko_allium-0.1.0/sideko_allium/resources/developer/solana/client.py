from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.solana.raw import AsyncRawClient, RawClient


class SolanaClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.raw = RawClient(base_client=self._base_client)


class AsyncSolanaClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.raw = AsyncRawClient(base_client=self._base_client)
