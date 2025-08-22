# explorer_metadata_tables

## Module Functions
### Get Table Metadata <a name="list"></a>



**API Endpoint**: `GET /api/v1/explorer/metadata/tables`

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.metadata.tables.list()

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.metadata.tables.list()

```

#### Response

##### Type
List of [TableMetadataResponseItem](/sideko_allium/types/models/table_metadata_response_item.py)

##### Example
`[{"catalog_name": "string", "schema_name": "string", "table_id": "string", "table_name": "string"}]`

### Get Table Metadata By Id <a name="get"></a>



**API Endpoint**: `GET /api/v1/explorer/metadata/tables/{table_id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `table_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.metadata.tables.get(table_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.metadata.tables.get(table_id="string")

```

#### Response

##### Type
[TableMetadataResponseItem](/sideko_allium/types/models/table_metadata_response_item.py)

##### Example
`{"catalog_name": "string", "schema_name": "string", "table_id": "string", "table_name": "string"}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

