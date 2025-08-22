# developer_trading_hyperliquid_info

## Module Functions
### Get Info <a name="get"></a>



**API Endpoint**: `POST /api/v1/developer/trading/hyperliquid/info`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ |  | `{}` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.trading.hyperliquid.info.get(data={})

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.trading.hyperliquid.info.get(data={})

```
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

