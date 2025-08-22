# developer_nfts_activities

## Module Functions
### NFT Activities by Contract Address <a name="list_by_contact_address"></a>

Fetch a list of NFT Activities by contract address.

**API Endpoint**: `GET /api/v1/developer/nfts/activities/{chain}/{contract_address}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `contract_address` | ✓ | Address of the NFT Contract. | `"string"` |
| `activity_types` | ✗ | Types of activities to fetch. | `["mint"]` |
| `cursor` | ✗ |  | `"string"` |
| `limit` | ✗ | Number of items to return in a response. | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.nfts.activities.list_by_contact_address(
    chain="abstract", contract_address="string"
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.nfts.activities.list_by_contact_address(
    chain="abstract", contract_address="string"
)

```

#### Response

##### Type
[ResponseEnvelopeMultiItemsNftActivity_](/sideko_allium/types/models/response_envelope_multi_items_nft_activity_.py)

##### Example
`{}`

### NFT Activities by Token ID <a name="list_by_token_id"></a>

Get a list of NFT Activities by token ID.

**API Endpoint**: `GET /api/v1/developer/nfts/activities/{chain}/{contract_address}/{token_id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `contract_address` | ✓ | Address of the NFT Contract. | `"string"` |
| `token_id` | ✓ | Token ID of the NFT. | `"string"` |
| `activity_types` | ✗ | Types of activities to fetch. | `["mint"]` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.nfts.activities.list_by_token_id(
    chain="abstract", contract_address="string", token_id="string"
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.nfts.activities.list_by_token_id(
    chain="abstract", contract_address="string", token_id="string"
)

```

#### Response

##### Type
[ResponseEnvelopeMultiItemsNftActivity_](/sideko_allium/types/models/response_envelope_multi_items_nft_activity_.py)

##### Example
`{}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

