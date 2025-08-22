# explorer_query_runs_error

## Module Functions
### Get Query Run Error <a name="get"></a>



**API Endpoint**: `GET /api/v1/explorer/query-runs/{run_id}/error`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `run_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.query_runs.error.get(run_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.query_runs.error.get(run_id="string")

```
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

