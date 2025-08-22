from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.nfts.users.tokens import (
    AsyncTokensClient,
    TokensClient,
)


class UsersClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.tokens = TokensClient(base_client=self._base_client)


class AsyncUsersClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.tokens = AsyncTokensClient(base_client=self._base_client)
