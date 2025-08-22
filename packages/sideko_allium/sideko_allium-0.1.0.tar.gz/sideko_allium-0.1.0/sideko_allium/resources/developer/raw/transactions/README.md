# developer_raw_transactions

## Module Functions
### Get Transactions <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/{chain}/raw/transactions`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `block_number` | ✗ |  | `123` |
| `from_address` | ✗ |  | `"string"` |
| `include_label` | ✗ |  | `True` |
| `order_by` | ✗ |  | `"asc"` |
| `order_by_col` | ✗ |  | `"string"` |
| `page` | ✗ | Page number | `123` |
| `size` | ✗ | Page size | `123` |
| `to_address` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.raw.transactions.list(chain="abstract")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.raw.transactions.list(chain="abstract")

```

#### Response

##### Type
[AlliumPageEnrichedTransaction_](/sideko_allium/types/models/allium_page_enriched_transaction_.py)

##### Example
`{"items": [{"block_hash": "string", "block_number": 123, "block_timestamp": "1970-01-01T00:00:00", "from_address": "string", "hash": "string", "nonce": 123, "transaction_index": 123, "value": "string"}], "size": 123}`

### Get Transaction <a name="get"></a>



**API Endpoint**: `GET /api/v1/developer/{chain}/raw/transactions/{transaction_hash}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `transaction_hash` | ✓ |  | `"string"` |
| `include_label` | ✗ |  | `True` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.raw.transactions.get(chain="abstract", transaction_hash="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.raw.transactions.get(
    chain="abstract", transaction_hash="string"
)

```

#### Response

##### Type
[EnrichedTransaction](/sideko_allium/types/models/enriched_transaction.py)

##### Example
`{"block_hash": "string", "block_number": 123, "block_timestamp": "1970-01-01T00:00:00", "from_address": "string", "hash": "string", "nonce": 123, "transaction_index": 123, "value": "string"}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

