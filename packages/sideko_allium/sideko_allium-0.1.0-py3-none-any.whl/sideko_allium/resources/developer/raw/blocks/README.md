# developer_raw_blocks

## Module Functions
### Get Blocks <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/{chain}/raw/blocks`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `page` | ✗ | Page number | `123` |
| `size` | ✗ | Page size | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.raw.blocks.list(chain="abstract")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.raw.blocks.list(chain="abstract")

```

#### Response

##### Type
[ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsEvmBlockTBlock_](/sideko_allium/types/models/api_server_app_core_pagination_allium_page_shared_lib_tortoise_models_evm_block_t_block_.py)

##### Example
`{"items": [{"hash": "string", "state_root": "string"}], "size": 123}`

### Get Block <a name="get"></a>



**API Endpoint**: `GET /api/v1/developer/{chain}/raw/blocks/{block_number}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `block_number` | ✓ |  | `"string"` |
| `chain` | ✓ |  | `"abstract"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.raw.blocks.get(block_number="string", chain="abstract")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.raw.blocks.get(block_number="string", chain="abstract")

```

#### Response

##### Type
[TortoiseContribPydanticCreatorSharedLibTortoiseModelsEvmBlockTBlock](/sideko_allium/types/models/tortoise_contrib_pydantic_creator_shared_lib_tortoise_models_evm_block_t_block.py)

##### Example
`{"hash": "string", "state_root": "string"}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

