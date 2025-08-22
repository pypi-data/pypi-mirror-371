from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.streams.data_management.filter_data_sources import (
    AsyncFilterDataSourcesClient,
    FilterDataSourcesClient,
)
from sideko_allium.resources.streams.data_management.filters import (
    AsyncFiltersClient,
    FiltersClient,
)
from sideko_allium.resources.streams.data_management.workflows import (
    AsyncWorkflowsClient,
    WorkflowsClient,
)


class DataManagementClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.filter_data_sources = FilterDataSourcesClient(
            base_client=self._base_client
        )
        self.filters = FiltersClient(base_client=self._base_client)
        self.workflows = WorkflowsClient(base_client=self._base_client)


class AsyncDataManagementClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.filter_data_sources = AsyncFilterDataSourcesClient(
            base_client=self._base_client
        )
        self.filters = AsyncFiltersClient(base_client=self._base_client)
        self.workflows = AsyncWorkflowsClient(base_client=self._base_client)
