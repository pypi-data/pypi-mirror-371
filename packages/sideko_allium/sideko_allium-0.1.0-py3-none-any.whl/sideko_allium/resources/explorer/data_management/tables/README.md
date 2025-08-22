# explorer_data_management_tables

## Module Functions
### Insert data into Explorer table <a name="insert"></a>

Insert rows into a private Explorer table controlled by your organization. If the table does not exist, it will be created.

**API Endpoint**: `POST /api/v1/explorer/data-management/tables/{table_name}/insert`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ |  | `[{}]` |
| `table_name` | ✓ |  | `"string"` |
| `overwrite` | ✗ |  | `True` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.data_management.tables.insert(data=[{}], table_name="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.data_management.tables.insert(
    data=[{}], table_name="string"
)

```

#### Response

##### Type
[IngestJob](/sideko_allium/types/models/ingest_job.py)

##### Example
`{"created_at": "1970-01-01T00:00:00", "creator_organization_id": "string", "job_id": "string", "overwrite": True, "table_name": "string", "updated_at": "1970-01-01T00:00:00"}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

