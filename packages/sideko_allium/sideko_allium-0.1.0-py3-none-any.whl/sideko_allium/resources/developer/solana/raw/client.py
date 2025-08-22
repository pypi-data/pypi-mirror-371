from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.solana.raw.blocks import (
    AsyncBlocksClient,
    BlocksClient,
)
from sideko_allium.resources.developer.solana.raw.inner_instructions import (
    AsyncInnerInstructionsClient,
    InnerInstructionsClient,
)
from sideko_allium.resources.developer.solana.raw.instructions import (
    AsyncInstructionsClient,
    InstructionsClient,
)
from sideko_allium.resources.developer.solana.raw.transaction_and_instructions import (
    AsyncTransactionAndInstructionsClient,
    TransactionAndInstructionsClient,
)
from sideko_allium.resources.developer.solana.raw.transactions import (
    AsyncTransactionsClient,
    TransactionsClient,
)


class RawClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.blocks = BlocksClient(base_client=self._base_client)
        self.inner_instructions = InnerInstructionsClient(base_client=self._base_client)
        self.instructions = InstructionsClient(base_client=self._base_client)
        self.transaction_and_instructions = TransactionAndInstructionsClient(
            base_client=self._base_client
        )
        self.transactions = TransactionsClient(base_client=self._base_client)


class AsyncRawClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.blocks = AsyncBlocksClient(base_client=self._base_client)
        self.inner_instructions = AsyncInnerInstructionsClient(
            base_client=self._base_client
        )
        self.instructions = AsyncInstructionsClient(base_client=self._base_client)
        self.transaction_and_instructions = AsyncTransactionAndInstructionsClient(
            base_client=self._base_client
        )
        self.transactions = AsyncTransactionsClient(base_client=self._base_client)
