# developer_nfts_collections

## Module Functions
### NFT Collections <a name="get"></a>

Fetch multiple collections that match the given contract addresses.

**API Endpoint**: `GET /api/v1/developer/nfts/collections/{chain}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `collection_symbols` | ✗ | Collection Symbols of the Solana NFT Collections to fetch. This is only used for Solana. | `["string"]` |
| `contract_addresses` | ✗ | Addresses of the NFT Contracts to fetch Collections for. This is used for EVM chains. | `["string"]` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.nfts.collections.get(chain="abstract")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.nfts.collections.get(chain="abstract")

```

#### Response

##### Type
[ResponseEnvelopeMultiItemsNftFullCollectionBase_](/sideko_allium/types/models/response_envelope_multi_items_nft_full_collection_base_.py)

##### Example
`{}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

