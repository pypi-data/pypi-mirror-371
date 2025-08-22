# developer_wallet_transactions

## Module Functions
### Transactions <a name="get"></a>

Provides enriched transaction history data for wallet(s).

**API Endpoint**: `POST /api/v1/developer/wallet/transactions`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ | List of chain+addresses to get transactions for. | `[{"address": "string", "chain": "string"}]` |
| `cursor` | ✗ |  | `"string"` |
| `limit` | ✗ | Limit the number of transactions returned. Default is 25. | `123` |
| `lookback_days` | ✗ |  | `123` |
| `transaction_hash` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.wallet.transactions.get(
    data=[
        {"address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", "chain": "ethereum"}
    ]
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.wallet.transactions.get(
    data=[
        {"address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", "chain": "ethereum"}
    ]
)

```

#### Response

##### Type
[WalletTransactionsEnvelope](/sideko_allium/types/models/wallet_transactions_envelope.py)

##### Example
`{"items": [{"activities": [{"approved_amount": {"raw_amount": "string"}, "asset": {"type_": "evm_erc1155"}, "contract_address": "string", "granularity": "collection", "spender_address": "string", "status": "approved", "transaction_hash": "string"}], "address": "string", "asset_transfers": [{"amount": {"raw_amount": "string"}, "asset": {"type_": "evm_erc1155"}, "from_address": "string", "to_address": "string", "transaction_hash": "string", "transfer_type": "burned"}], "block_hash": "string", "block_number": 123, "block_timestamp": "1970-01-01T00:00:00", "chain": "string", "fee": {"raw_amount": "string"}, "from_address": "string", "hash": "string", "id": "string", "index": 123, "labels": ["string"], "to_address": "string", "type_": 123, "within_block_order_key": 123}]}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

