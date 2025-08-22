# developer_bitcoin_mempool_outputs

## Module Functions
### Get Mempool Outputs <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/bitcoin/mempool/outputs`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `fetched_at_gte` | ✗ |  | `"1970-01-01T00:00:00"` |
| `fetched_at_lte` | ✗ |  | `"1970-01-01T00:00:00"` |
| `page` | ✗ | Page number | `123` |
| `size` | ✗ | Page size | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.bitcoin.mempool.outputs.list(chain="abstract")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.bitcoin.mempool.outputs.list(chain="abstract")

```

#### Response

##### Type
[AlliumPageTMempoolOutput_](/sideko_allium/types/models/allium_page_t_mempool_output_.py)

##### Example
`{"items": [{"utxo_id": "string"}], "size": 123}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

