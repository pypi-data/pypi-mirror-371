# developer_bitcoin_ordinals_inscription_transfers

## Module Functions
### Get Ordinals Inscription Transfers <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/bitcoin/ordinals/inscription-transfers`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `block_number` | ✗ |  | `"string"` |
| `page` | ✗ | Page number | `123` |
| `size` | ✗ | Page size | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.bitcoin.ordinals.inscription_transfers.list(chain="abstract")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.bitcoin.ordinals.inscription_transfers.list(
    chain="abstract"
)

```

#### Response

##### Type
[AlliumPageTOrdinalsInscriptionTransfer_](/sideko_allium/types/models/allium_page_t_ordinals_inscription_transfer_.py)

##### Example
`{"items": [{"inscription_id": "string"}], "size": 123}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

