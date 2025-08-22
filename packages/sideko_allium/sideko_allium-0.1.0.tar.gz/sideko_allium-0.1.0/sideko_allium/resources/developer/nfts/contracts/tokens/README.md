# developer_nfts_contracts_tokens

## Module Functions
### NFT Tokens by Contract <a name="list"></a>

This API returns all NFT tokens that belong to a given contract.

**API Endpoint**: `GET /api/v1/developer/nfts/contracts/{chain}/{contract_address}/tokens`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `contract_address` | ✓ |  | `"string"` |
| `cursor` | ✗ |  | `"string"` |
| `limit` | ✗ | Number of items to return in a response | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.nfts.contracts.tokens.list(
    chain="abstract", contract_address="string"
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.nfts.contracts.tokens.list(
    chain="abstract", contract_address="string"
)

```

#### Response

##### Type
[ResponseEnvelopeMultiItemsNftToken_](/sideko_allium/types/models/response_envelope_multi_items_nft_token_.py)

##### Example
`{}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

