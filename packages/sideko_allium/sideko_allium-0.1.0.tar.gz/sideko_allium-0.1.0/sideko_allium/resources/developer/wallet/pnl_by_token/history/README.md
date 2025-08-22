# developer_wallet_pnl_by_token_history

## Module Functions
### Get Pnl By Token With Historical Breakdown <a name="get"></a>



**API Endpoint**: `POST /api/v1/developer/wallet/pnl-by-token/history`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `addresses` | ✓ |  | `[{"address": "string", "chain": "string", "token_address": "string"}]` |
| `end_timestamp` | ✓ |  | `"1970-01-01T00:00:00"` |
| `granularity` | ✓ |  | `"1d"` |
| `start_timestamp` | ✓ |  | `"1970-01-01T00:00:00"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.wallet.pnl_by_token.history.get(
    addresses=[
        {
            "address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp",
            "chain": "solana",
            "token_address": "So11111111111111111111111111111111111111112",
        }
    ],
    end_timestamp="2025-04-10T00:00:00Z",
    granularity="1h",
    start_timestamp="2025-04-01T00:00:00Z",
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.wallet.pnl_by_token.history.get(
    addresses=[
        {
            "address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp",
            "chain": "solana",
            "token_address": "So11111111111111111111111111111111111111112",
        }
    ],
    end_timestamp="2025-04-10T00:00:00Z",
    granularity="1h",
    start_timestamp="2025-04-01T00:00:00Z",
)

```

#### Response

##### Type
[ResponseEnvelopeUnionHistoricalPnlByTokenNoneType_](/sideko_allium/types/models/response_envelope_union_historical_pnl_by_token_none_type_.py)

##### Example
`{}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

