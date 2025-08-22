# developer_wallet_balances

## Module Functions
### Latest Fungible Token Balances <a name="get"></a>

Get the latest balances for a list of wallets.

**API Endpoint**: `POST /api/v1/developer/wallet/balances`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ | List of wallet chain+address pairs to get balances for. | `[{"address": "string", "chain": "string"}]` |
| `with_liquidity_info` | ✗ | If true, returns total_liquidity_usd as well. See https://docs.allium.so/developer/data-tips#token-liquidity for more details. | `True` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.wallet.balances.get(
    data=[{"address": "string", "chain": "string"}]
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.wallet.balances.get(
    data=[{"address": "string", "chain": "string"}]
)

```

#### Response

##### Type
[WalletLatestBalancesNewEnvelope](/sideko_allium/types/models/wallet_latest_balances_new_envelope.py)

##### Example
`{"items": [{"address": "string", "block_timestamp": "1970-01-01T00:00:00", "chain": "string", "raw_balance": 123, "token": {"address": "string", "chain": "string", "type_": "evm_erc1155"}}]}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

## Submodules
- [history](history/README.md) - history

