from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.supported_chains.realtime_apis import (
    AsyncRealtimeApisClient,
    RealtimeApisClient,
)


class SupportedChainsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.realtime_apis = RealtimeApisClient(base_client=self._base_client)


class AsyncSupportedChainsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.realtime_apis = AsyncRealtimeApisClient(base_client=self._base_client)
