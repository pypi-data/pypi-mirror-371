# developer_wallet_balances_history

## Module Functions
### Historical Fungible Token Balances <a name="get"></a>

Get the historical balances for a list of wallets.

**API Endpoint**: `POST /api/v1/developer/wallet/balances/history`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `addresses` | ✓ |  | `[{"address": "string", "chain": "string"}]` |
| `end_timestamp` | ✓ |  | `"1970-01-01T00:00:00"` |
| `start_timestamp` | ✓ |  | `"1970-01-01T00:00:00"` |
| `cursor` | ✗ |  | `"string"` |
| `limit` | ✗ | Max number of items returned. Default is 1000. | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.wallet.balances.history.get(
    addresses=[
        {"address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp", "chain": "solana"}
    ],
    end_timestamp="2025-04-01T13:00:00Z",
    start_timestamp="2025-04-01T12:00:00Z",
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.wallet.balances.history.get(
    addresses=[
        {"address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp", "chain": "solana"}
    ],
    end_timestamp="2025-04-01T13:00:00Z",
    start_timestamp="2025-04-01T12:00:00Z",
)

```

#### Response

##### Type
[ApiServerAppServicesWalletBalancesWalletHistoricalBalancesClientEnvelope](/sideko_allium/types/models/api_server_app_services_wallet_balances_wallet_historical_balances_client_envelope.py)

##### Example
`{"items": [{"address": "string", "block_hash": "string", "block_slot": 123, "block_timestamp": "1970-01-01T00:00:00", "chain": "string", "raw_balance": 123, "token": {"address": "string", "chain": "string", "type_": "evm_erc1155"}, "token_account": "string", "txn_id": "string", "txn_index": 123}]}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

