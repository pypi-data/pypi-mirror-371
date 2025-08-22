# developer_prices_stats

## Module Functions
### Token Stats <a name="get"></a>

Get the stats for the given token addresseses.

**API Endpoint**: `POST /api/v1/developer/prices/stats`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ | List of token addresses to get stats for. | `[{"chain": "string", "token_address": "string"}]` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.prices.stats.get(
    data=[{"chain": "string", "token_address": "string"}]
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.prices.stats.get(
    data=[{"chain": "string", "token_address": "string"}]
)

```

#### Response

##### Type
[EnvelopeTokenStats_](/sideko_allium/types/models/envelope_token_stats_.py)

##### Example
`{"items": [{"chain": "string", "decimals": 123, "high_1h": 123.0, "high_24h": 123.0, "high_all_time": 123.0, "latest_price": 123.0, "low_1h": 123.0, "low_24h": 123.0, "low_all_time": 123.0, "mint": "string", "percent_change_1h": 123.0, "percent_change_24h": 123.0, "timestamp": "1970-01-01T00:00:00", "volume_1h": 123.0, "volume_24h": 123.0}]}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

