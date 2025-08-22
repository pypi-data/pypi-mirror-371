# developer_solana_raw_blocks

## Module Functions
### Get Blocks <a name="list"></a>



**API Endpoint**: `GET /api/v1/developer/solana/raw/blocks`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `page` | ✗ | Page number | `123` |
| `size` | ✗ | Page size | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.solana.raw.blocks.list()

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.solana.raw.blocks.list()

```

#### Response

##### Type
[ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsSolanaBlockTBlock_](/sideko_allium/types/models/api_server_app_core_pagination_allium_page_shared_lib_tortoise_models_solana_block_t_block_.py)

##### Example
`{"items": [{"slot": 123}], "size": 123}`

### Get Block <a name="get"></a>



**API Endpoint**: `GET /api/v1/developer/solana/raw/blocks/{block_slot}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `block_slot` | ✓ |  | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.solana.raw.blocks.get(block_slot=123)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.solana.raw.blocks.get(block_slot=123)

```

#### Response

##### Type
[TortoiseContribPydanticCreatorSharedLibTortoiseModelsSolanaBlockTBlock](/sideko_allium/types/models/tortoise_contrib_pydantic_creator_shared_lib_tortoise_models_solana_block_t_block.py)

##### Example
`{"slot": 123}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

