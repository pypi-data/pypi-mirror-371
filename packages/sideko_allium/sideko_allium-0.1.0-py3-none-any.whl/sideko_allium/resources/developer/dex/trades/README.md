# developer_dex_trades

## Module Functions
### Get Trades <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/{chain}/dex/trades`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `block_number` | ✗ |  | `"string"` |
| `transaction_hash` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.dex.trades.list(chain="abstract")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.dex.trades.list(chain="abstract")

```

#### Response

##### Type
List of [TdexTrade](/sideko_allium/types/models/tdex_trade.py)

##### Example
`[{"block_hash": "string", "block_number": 123, "block_timestamp": "1970-01-01T00:00:00", "liquidity_pool_address": "string", "log_index": 123, "sender_address": "string", "to_address": "string", "token_bought_amount_raw": 123, "token_sold_amount_raw": 123, "transaction_from_address": "string", "transaction_hash": "string", "transaction_to_address": "string"}]`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

