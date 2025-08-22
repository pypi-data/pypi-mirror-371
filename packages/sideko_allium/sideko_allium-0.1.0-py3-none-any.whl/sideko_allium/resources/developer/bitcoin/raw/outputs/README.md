# developer_bitcoin_raw_outputs

## Module Functions
### Get Outputs <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/bitcoin/raw/outputs`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `block_number` | ✗ |  | `"string"` |
| `page` | ✗ | Page number | `123` |
| `size` | ✗ | Page size | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.bitcoin.raw.outputs.list()

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.bitcoin.raw.outputs.list()

```

#### Response

##### Type
[AlliumPageTOutput_](/sideko_allium/types/models/allium_page_t_output_.py)

##### Example
`{"items": [{"address": "string", "address0": "string", "addresses": "string", "block_hash": "string", "block_number": 123, "block_timestamp": "1970-01-01T00:00:00", "description": "string", "fetched_at": "1970-01-01T00:00:00", "index": 123, "is_patched_block": True, "is_reorg": True, "script_asm": "string", "script_hex": "string", "transaction_hash": "string", "transaction_index": 123, "type_": "string", "utxo_id": "string", "value": "string", "value_max_exclusive": "string", "value_min_inclusive": "string"}], "size": 123}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

