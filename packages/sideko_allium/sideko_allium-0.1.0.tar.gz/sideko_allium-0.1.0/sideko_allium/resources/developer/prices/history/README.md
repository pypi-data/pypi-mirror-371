# developer_prices_history

## Module Functions
### Token Prices History <a name="list"></a>

Get a list of historical token prices by chain and token address for a given time range and granularity.

**API Endpoint**: `POST /api/v1/developer/prices/history`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ |  | `{"addresses": [{"chain": "string", "token_address": "string"}, {"chain": "string", "token_address": "string"}], "end_timestamp": "2025-03-07T01:00:00Z", "start_timestamp": "2025-03-07T00:00:00Z", "time_granularity": "5m"}` |
| `cursor` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.prices.history.list(
    data={
        "addresses": [
            {"chain": "string", "token_address": "string"},
            {"chain": "string", "token_address": "string"},
        ],
        "end_timestamp": "2025-03-07T01:00:00Z",
        "start_timestamp": "2025-03-07T00:00:00Z",
        "time_granularity": "5m",
    }
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.prices.history.list(
    data={
        "addresses": [
            {"chain": "string", "token_address": "string"},
            {"chain": "string", "token_address": "string"},
        ],
        "end_timestamp": "2025-03-07T01:00:00Z",
        "start_timestamp": "2025-03-07T00:00:00Z",
        "time_granularity": "5m",
    }
)

```

#### Response

##### Type
[EnvelopeUnionTokenPriceHistoricalTokenPrice_](/sideko_allium/types/models/envelope_union_token_price_historical_token_price_.py)

##### Example
`{"items": [{"chain": "string", "decimals": 123, "mint": "string", "prices": [{"close": 123.0, "high": 123.0, "low": 123.0, "open": 123.0, "price": 123.0, "timestamp": "1970-01-01T00:00:00"}]}]}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

