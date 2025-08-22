from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.explorer.data_management.ingest_jobs import (
    AsyncIngestJobsClient,
    IngestJobsClient,
)
from sideko_allium.resources.explorer.data_management.tables import (
    AsyncTablesClient,
    TablesClient,
)


class DataManagementClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.ingest_jobs = IngestJobsClient(base_client=self._base_client)
        self.tables = TablesClient(base_client=self._base_client)


class AsyncDataManagementClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.ingest_jobs = AsyncIngestJobsClient(base_client=self._base_client)
        self.tables = AsyncTablesClient(base_client=self._base_client)
