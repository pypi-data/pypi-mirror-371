# developer_bitcoin_raw_transactions

## Module Functions
### Get Transactions <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/bitcoin/raw/transactions`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `block_hash` | ✗ |  | `"string"` |
| `page` | ✗ | Page number | `123` |
| `size` | ✗ | Page size | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.bitcoin.raw.transactions.list()

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.bitcoin.raw.transactions.list()

```

#### Response

##### Type
[AlliumPageTTransaction_](/sideko_allium/types/models/allium_page_t_transaction_.py)

##### Example
`{"items": [{"block_hash": "string", "block_number": 123, "block_timestamp": "1970-01-01T00:00:00", "fee": 123.0, "hash": "string", "index": 123, "input_count": 123, "is_coinbase": True, "lock_time": 123, "output_count": 123, "output_value": 123.0, "size": 123, "version": 123, "virtual_size": 123}], "size": 123}`

### Get Transaction <a name="get"></a>



**API Endpoint**: `GET /api/v1/developer/bitcoin/raw/transactions/{transaction_hash}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `transaction_hash` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.bitcoin.raw.transactions.get(transaction_hash="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.bitcoin.raw.transactions.get(transaction_hash="string")

```

#### Response

##### Type
[TTransaction](/sideko_allium/types/models/t_transaction.py)

##### Example
`{"block_hash": "string", "block_number": 123, "block_timestamp": "1970-01-01T00:00:00", "fee": 123.0, "hash": "string", "index": 123, "input_count": 123, "is_coinbase": True, "lock_time": 123, "output_count": 123, "output_value": 123.0, "size": 123, "version": 123, "virtual_size": 123}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

