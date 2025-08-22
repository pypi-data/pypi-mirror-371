# developer_raw_erc1155_tokens

## Module Functions
### Get Erc1155 Tokens <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/{chain}/raw/erc1155-tokens`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `address` | ✗ |  | `"string"` |
| `block_number` | ✗ |  | `"string"` |
| `order_by` | ✗ |  | `"asc"` |
| `order_by_col` | ✗ |  | `"string"` |
| `page` | ✗ | Page number | `123` |
| `size` | ✗ | Page size | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.raw.erc1155_tokens.list(chain="abstract")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.raw.erc1155_tokens.list(chain="abstract")

```

#### Response

##### Type
[AlliumPageTerc1155Token_](/sideko_allium/types/models/allium_page_terc1155_token_.py)

##### Example
`{"items": [{"address": "string", "block_timestamp": "1970-01-01T00:00:00", "name": "string", "symbol": "string"}], "size": 123}`

### Get Erc1155 Token <a name="get"></a>



**API Endpoint**: `GET /api/v1/developer/{chain}/raw/erc1155-tokens/{address}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `address` | ✓ |  | `"string"` |
| `chain` | ✓ |  | `"abstract"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.raw.erc1155_tokens.get(address="string", chain="abstract")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.raw.erc1155_tokens.get(address="string", chain="abstract")

```

#### Response

##### Type
[Terc1155Token](/sideko_allium/types/models/terc1155_token.py)

##### Example
`{"address": "string", "block_timestamp": "1970-01-01T00:00:00", "name": "string", "symbol": "string"}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

