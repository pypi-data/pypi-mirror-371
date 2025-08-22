# explorer_data_management_ingest_jobs_status

## Module Functions
### Ingest Job Status <a name="list"></a>



**API Endpoint**: `GET /api/v1/explorer/data-management/ingest-jobs/{job_id}/status`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `job_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.data_management.ingest_jobs.status.list(job_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.data_management.ingest_jobs.status.list(job_id="string")

```
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

