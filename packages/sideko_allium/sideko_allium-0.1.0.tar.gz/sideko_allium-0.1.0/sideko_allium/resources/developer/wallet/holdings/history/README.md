# developer_wallet_holdings_history

## Module Functions
### Get Holdings History <a name="get"></a>



**API Endpoint**: `POST /api/v1/developer/wallet/holdings/history`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `addresses` | ✓ |  | `[{"address": "string", "chain": "string"}]` |
| `end_timestamp` | ✓ |  | `"1970-01-01T00:00:00"` |
| `granularity` | ✓ |  | `"15s"` |
| `start_timestamp` | ✓ |  | `"1970-01-01T00:00:00"` |
| `cursor` | ✗ |  | `"string"` |
| `include_token_breakdown` | ✗ |  | `True` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.wallet.holdings.history.get(
    addresses=[
        {"address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp", "chain": "solana"}
    ],
    end_timestamp="2025-04-10T00:00:00Z",
    granularity="1h",
    start_timestamp="2025-04-01T00:00:00Z",
    include_token_breakdown=False,
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.wallet.holdings.history.get(
    addresses=[
        {"address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp", "chain": "solana"}
    ],
    end_timestamp="2025-04-10T00:00:00Z",
    granularity="1h",
    start_timestamp="2025-04-01T00:00:00Z",
    include_token_breakdown=False,
)

```

#### Response

##### Type
[ApiServerAppServicesHoldingsCommonModelsEnvelope](/sideko_allium/types/models/api_server_app_services_holdings_common_models_envelope.py)

##### Example
`{"items": [{"amount": {"amount": 123.0, "currency": "USD"}, "timestamp": "1970-01-01T00:00:00"}]}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

