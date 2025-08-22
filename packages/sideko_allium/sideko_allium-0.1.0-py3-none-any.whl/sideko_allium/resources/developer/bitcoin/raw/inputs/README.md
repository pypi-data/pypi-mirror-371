# developer_bitcoin_raw_inputs

## Module Functions
### Get Inputs <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/bitcoin/raw/inputs`

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
res = client.developer.bitcoin.raw.inputs.list()

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.bitcoin.raw.inputs.list()

```

#### Response

##### Type
[AlliumPageTInput_](/sideko_allium/types/models/allium_page_t_input_.py)

##### Example
`{"items": [{"input_id": "string"}], "size": 123}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

