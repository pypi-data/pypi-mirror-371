# developer_trading_hyperliquid_orderbook_snapshot

## Module Functions
### Orderbook Snapshot <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/trading/hyperliquid/orderbook/snapshot`

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.trading.hyperliquid.orderbook.snapshot.list()

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.trading.hyperliquid.orderbook.snapshot.list()

```
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

