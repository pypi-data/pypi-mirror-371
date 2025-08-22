# developer_nfts_contracts

## Module Functions
### NFT Contract <a name="get_metadata"></a>

This API returns the NFT contract metadata associated with the contract address.

**API Endpoint**: `GET /api/v1/developer/nfts/contracts/{chain}/{contract_address}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `contract_address` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.nfts.contracts.get_metadata(
    chain="abstract", contract_address="string"
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.nfts.contracts.get_metadata(
    chain="abstract", contract_address="string"
)

```

#### Response

##### Type
[ResponseEnvelopeSingleItemNftContract_](/sideko_allium/types/models/response_envelope_single_item_nft_contract_.py)

##### Example
`{}`

### NFT Token by Contract and Token ID <a name="get_by_contract_and_token_id"></a>

This API returns NFT token metadata by contract and token ID. For Solana, pass in a token ID of 0.

**API Endpoint**: `GET /api/v1/developer/nfts/contracts/{chain}/{contract_address}/{token_id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `contract_address` | ✓ |  | `"string"` |
| `token_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.nfts.contracts.get_by_contract_and_token_id(
    chain="abstract", contract_address="string", token_id="string"
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.nfts.contracts.get_by_contract_and_token_id(
    chain="abstract", contract_address="string", token_id="string"
)

```

#### Response

##### Type
[ResponseEnvelopeSingleItemNftToken_](/sideko_allium/types/models/response_envelope_single_item_nft_token_.py)

##### Example
`{}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

## Submodules
- [tokens](tokens/README.md) - tokens

