# developer_wallet_nft_collections

## Module Functions
### NFT Collections owned by wallet <a name="get"></a>

Get all NFT collections owned by a wallet

**API Endpoint**: `POST /api/v1/developer/wallet/nft-collections`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `address` | ✓ |  | `"string"` |
| `chain` | ✓ |  | `"string"` |
| `cursor` | ✗ |  | `"string"` |
| `limit` | ✗ | Number of items to return in a response. | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.wallet.nft_collections.get(address="string", chain="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.wallet.nft_collections.get(
    address="string", chain="string"
)

```

#### Response

##### Type
List of [NftCollection](/sideko_allium/types/models/nft_collection.py)

##### Example
`[{}]`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

