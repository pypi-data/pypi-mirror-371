from sideko_allium.core import AsyncBaseClient, SyncBaseClient
from sideko_allium.resources.developer.bitcoin.ordinals.inscription_mints import (
    AsyncInscriptionMintsClient,
    InscriptionMintsClient,
)
from sideko_allium.resources.developer.bitcoin.ordinals.inscription_transfers import (
    AsyncInscriptionTransfersClient,
    InscriptionTransfersClient,
)
from sideko_allium.resources.developer.bitcoin.ordinals.token_transfers import (
    AsyncTokenTransfersClient,
    TokenTransfersClient,
)


class OrdinalsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.inscription_mints = InscriptionMintsClient(base_client=self._base_client)
        self.inscription_transfers = InscriptionTransfersClient(
            base_client=self._base_client
        )
        self.token_transfers = TokenTransfersClient(base_client=self._base_client)


class AsyncOrdinalsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.inscription_mints = AsyncInscriptionMintsClient(
            base_client=self._base_client
        )
        self.inscription_transfers = AsyncInscriptionTransfersClient(
            base_client=self._base_client
        )
        self.token_transfers = AsyncTokenTransfersClient(base_client=self._base_client)
