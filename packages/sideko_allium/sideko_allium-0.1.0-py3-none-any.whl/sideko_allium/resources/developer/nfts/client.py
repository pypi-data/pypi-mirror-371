from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.nfts.activities import (
    ActivitiesClient,
    AsyncActivitiesClient,
)
from sideko_allium.resources.developer.nfts.collections import (
    AsyncCollectionsClient,
    CollectionsClient,
)
from sideko_allium.resources.developer.nfts.contracts import (
    AsyncContractsClient,
    ContractsClient,
)
from sideko_allium.resources.developer.nfts.listings import (
    AsyncListingsClient,
    ListingsClient,
)
from sideko_allium.resources.developer.nfts.users import AsyncUsersClient, UsersClient


class NftsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.activities = ActivitiesClient(base_client=self._base_client)
        self.collections = CollectionsClient(base_client=self._base_client)
        self.contracts = ContractsClient(base_client=self._base_client)
        self.listings = ListingsClient(base_client=self._base_client)
        self.users = UsersClient(base_client=self._base_client)


class AsyncNftsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.activities = AsyncActivitiesClient(base_client=self._base_client)
        self.collections = AsyncCollectionsClient(base_client=self._base_client)
        self.contracts = AsyncContractsClient(base_client=self._base_client)
        self.listings = AsyncListingsClient(base_client=self._base_client)
        self.users = AsyncUsersClient(base_client=self._base_client)
