from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.explorer.data_management import (
    AsyncDataManagementClient,
    DataManagementClient,
)
from sideko_allium.resources.explorer.metadata import (
    AsyncMetadataClient,
    MetadataClient,
)
from sideko_allium.resources.explorer.queries import AsyncQueriesClient, QueriesClient
from sideko_allium.resources.explorer.query_runs import (
    AsyncQueryRunsClient,
    QueryRunsClient,
)
from sideko_allium.resources.explorer.workflows import (
    AsyncWorkflowsClient,
    WorkflowsClient,
)


class ExplorerClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.data_management = DataManagementClient(base_client=self._base_client)
        self.metadata = MetadataClient(base_client=self._base_client)
        self.query_runs = QueryRunsClient(base_client=self._base_client)
        self.queries = QueriesClient(base_client=self._base_client)
        self.workflows = WorkflowsClient(base_client=self._base_client)


class AsyncExplorerClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.data_management = AsyncDataManagementClient(base_client=self._base_client)
        self.metadata = AsyncMetadataClient(base_client=self._base_client)
        self.query_runs = AsyncQueryRunsClient(base_client=self._base_client)
        self.queries = AsyncQueriesClient(base_client=self._base_client)
        self.workflows = AsyncWorkflowsClient(base_client=self._base_client)
