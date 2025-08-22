# developer_bitcoin_ordinals_inscription_mints

## Module Functions
### Get Ordinals Inscription Mints <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/bitcoin/ordinals/inscription-mints`

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
res = client.developer.bitcoin.ordinals.inscription_mints.list(chain="abstract")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.bitcoin.ordinals.inscription_mints.list(chain="abstract")

```

#### Response

##### Type
[AlliumPageTOrdinalsInscriptionMint_](/sideko_allium/types/models/allium_page_t_ordinals_inscription_mint_.py)

##### Example
`{"items": [{"inscription_id": "string"}], "size": 123}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

