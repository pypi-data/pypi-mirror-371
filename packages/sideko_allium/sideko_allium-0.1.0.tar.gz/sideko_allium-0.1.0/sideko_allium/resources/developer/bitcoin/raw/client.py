from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.bitcoin.raw.blocks import (
    AsyncBlocksClient,
    BlocksClient,
)
from sideko_allium.resources.developer.bitcoin.raw.inputs import (
    AsyncInputsClient,
    InputsClient,
)
from sideko_allium.resources.developer.bitcoin.raw.outputs import (
    AsyncOutputsClient,
    OutputsClient,
)
from sideko_allium.resources.developer.bitcoin.raw.transactions import (
    AsyncTransactionsClient,
    TransactionsClient,
)


class RawClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.blocks = BlocksClient(base_client=self._base_client)
        self.inputs = InputsClient(base_client=self._base_client)
        self.outputs = OutputsClient(base_client=self._base_client)
        self.transactions = TransactionsClient(base_client=self._base_client)


class AsyncRawClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.blocks = AsyncBlocksClient(base_client=self._base_client)
        self.inputs = AsyncInputsClient(base_client=self._base_client)
        self.outputs = AsyncOutputsClient(base_client=self._base_client)
        self.transactions = AsyncTransactionsClient(base_client=self._base_client)
