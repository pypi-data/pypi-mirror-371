from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.explorer.metadata.tables import (
    AsyncTablesClient,
    TablesClient,
)


class MetadataClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.tables = TablesClient(base_client=self._base_client)


class AsyncMetadataClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.tables = AsyncTablesClient(base_client=self._base_client)
