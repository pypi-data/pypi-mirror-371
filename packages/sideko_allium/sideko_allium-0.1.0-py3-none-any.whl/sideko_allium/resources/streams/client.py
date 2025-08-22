from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.streams.data_management import (
    AsyncDataManagementClient,
    DataManagementClient,
)


class StreamsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.data_management = DataManagementClient(base_client=self._base_client)


class AsyncStreamsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.data_management = AsyncDataManagementClient(base_client=self._base_client)
