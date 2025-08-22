from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.admin.data_transformations import (
    AsyncDataTransformationsClient,
    DataTransformationsClient,
)


class AdminClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.data_transformations = DataTransformationsClient(
            base_client=self._base_client
        )


class AsyncAdminClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.data_transformations = AsyncDataTransformationsClient(
            base_client=self._base_client
        )
