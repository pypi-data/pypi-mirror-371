# developer_wallet_latest_nft_balances

## Module Functions
### Latest NFT Balances <a name="get"></a>

Get the latest NFT balances for a list of wallets.

**API Endpoint**: `POST /api/v1/developer/wallet/latest-nft-balances`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ | List of wallet chain+address pairs to get balances for. | `[{"address": "string", "chain": "string"}]` |
| `cursor` | ✗ |  | `"string"` |
| `exclude_spam` | ✗ | Exclude spam NFTs | `True` |
| `limit` | ✗ | Number of items to return in a response. | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.wallet.latest_nft_balances.get(
    data=[{"address": "string", "chain": "string"}]
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.wallet.latest_nft_balances.get(
    data=[{"address": "string", "chain": "string"}]
)

```

#### Response

##### Type
List of [WalletNftLatestBalance](/sideko_allium/types/models/wallet_nft_latest_balance.py)

##### Example
`[{"address": "string", "balance": 123, "chain": "string", "token_address": "string", "token_id": "string"}]`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

