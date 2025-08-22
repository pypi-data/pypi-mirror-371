# explorer_data_management_ingest_jobs

## Module Functions
### Get Ingest Jobs <a name="list"></a>



**API Endpoint**: `GET /api/v1/explorer/data-management/ingest-jobs`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `status` | ✗ |  | `"completed"` |
| `table_name` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.data_management.ingest_jobs.list()

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.data_management.ingest_jobs.list()

```

#### Response

##### Type
List of [IngestJob](/sideko_allium/types/models/ingest_job.py)

##### Example
`[{"created_at": "1970-01-01T00:00:00", "creator_organization_id": "string", "job_id": "string", "overwrite": True, "table_name": "string", "updated_at": "1970-01-01T00:00:00"}]`

### Get Ingest Job <a name="get"></a>



**API Endpoint**: `GET /api/v1/explorer/data-management/ingest-jobs/{job_id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `job_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.data_management.ingest_jobs.get(job_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.data_management.ingest_jobs.get(job_id="string")

```

#### Response

##### Type
[IngestJob](/sideko_allium/types/models/ingest_job.py)

##### Example
`{"created_at": "1970-01-01T00:00:00", "creator_organization_id": "string", "job_id": "string", "overwrite": True, "table_name": "string", "updated_at": "1970-01-01T00:00:00"}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

## Submodules
- [status](status/README.md) - status

