from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.raw.blocks import AsyncBlocksClient, BlocksClient
from sideko_allium.resources.developer.raw.erc1155_tokens import (
    AsyncErc1155TokensClient,
    Erc1155TokensClient,
)
from sideko_allium.resources.developer.raw.erc20_tokens import (
    AsyncErc20TokensClient,
    Erc20TokensClient,
)
from sideko_allium.resources.developer.raw.erc721_tokens import (
    AsyncErc721TokensClient,
    Erc721TokensClient,
)
from sideko_allium.resources.developer.raw.transactions import (
    AsyncTransactionsClient,
    TransactionsClient,
)


class RawClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.blocks = BlocksClient(base_client=self._base_client)
        self.erc1155_tokens = Erc1155TokensClient(base_client=self._base_client)
        self.erc20_tokens = Erc20TokensClient(base_client=self._base_client)
        self.erc721_tokens = Erc721TokensClient(base_client=self._base_client)
        self.transactions = TransactionsClient(base_client=self._base_client)


class AsyncRawClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.blocks = AsyncBlocksClient(base_client=self._base_client)
        self.erc1155_tokens = AsyncErc1155TokensClient(base_client=self._base_client)
        self.erc20_tokens = AsyncErc20TokensClient(base_client=self._base_client)
        self.erc721_tokens = AsyncErc721TokensClient(base_client=self._base_client)
        self.transactions = AsyncTransactionsClient(base_client=self._base_client)
