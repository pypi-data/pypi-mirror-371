# developer_solana_raw_transactions

## Module Functions
### Get Transactions <a name="get"></a>



**API Endpoint**: `POST /api/v1/developer/solana/raw/transactions`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ |  | `[{"block_timestamp": "1970-01-01T00:00:00", "txn_id": "string"}]` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.solana.raw.transactions.get(
    data=[{"block_timestamp": "1970-01-01T00:00:00", "txn_id": "string"}]
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.solana.raw.transactions.get(
    data=[{"block_timestamp": "1970-01-01T00:00:00", "txn_id": "string"}]
)

```

#### Response

##### Type
List of [Transaction](/sideko_allium/types/models/transaction.py)

##### Example
`[{"account_keys": [{"pubkey": "string", "signer": True, "source": "string", "writable": True}], "block_hash": "string", "block_height": 123, "block_slot": 123, "block_timestamp": "1970-01-01T00:00:00", "fee": 123, "instruction_count": 123, "is_voting": True, "log_messages": ["string"], "mint_to_decimals": {}, "post_balances": [123], "post_token_balances": [{"account": "string", "account_index": 123, "amount": "string", "decimals": 123, "mint": "string", "owner": "string"}], "pre_balances": [123], "pre_token_balances": [{"account": "string", "account_index": 123, "amount": "string", "decimals": 123, "mint": "string", "owner": "string"}], "pubkeys": ["string"], "recent_block_hash": "string", "signatures": ["string"], "signer": "string", "sol_amounts": {}, "success": True, "token_accounts": {}, "txn_id": "string", "txn_index": 123}]`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

