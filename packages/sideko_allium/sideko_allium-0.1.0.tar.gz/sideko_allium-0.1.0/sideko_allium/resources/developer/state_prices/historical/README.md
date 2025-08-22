# developer_state_prices_historical

## Module Functions
### Get State Prices <a name="list"></a>

Get state prices for a given chain and base asset address. Supports both single timestamp queries and time range queries.

**API Endpoint**: `POST /api/v1/developer/state-prices/historical`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `base_asset_address` | ✓ | The base asset address | `"string"` |
| `chain` | ✓ | The blockchain name (e.g., 'ethereum', 'solana') | `"string"` |
| `end_timestamp` | ✗ |  | `"string"` |
| `start_timestamp` | ✗ |  | `"string"` |
| `timestamp` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.state_prices.historical.list(
    base_asset_address="string", chain="string"
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.state_prices.historical.list(
    base_asset_address="string", chain="string"
)

```

#### Response

##### Type
[ResponseEnvelopeMultiItemsLiquidityPoolStateData_](/sideko_allium/types/models/response_envelope_multi_items_liquidity_pool_state_data_.py)

##### Example
`{}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

