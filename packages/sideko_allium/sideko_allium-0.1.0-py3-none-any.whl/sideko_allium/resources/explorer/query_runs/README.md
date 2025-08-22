# explorer_query_runs

## Module Functions
### Get Latest Query Run Handler <a name="list"></a>



**API Endpoint**: `GET /api/v1/explorer/query-runs`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `query_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.query_runs.list(query_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.query_runs.list(query_id="string")

```

#### Response

##### Type
[QueryRun](/sideko_allium/types/models/query_run.py)

##### Example
`{"created_at": "1970-01-01T00:00:00", "creator_id": "string", "query_config": {"limit": 123, "sql": "string"}, "query_id": "string", "run_id": "string", "status": "canceled"}`

### Get Query Run Handler <a name="get"></a>



**API Endpoint**: `GET /api/v1/explorer/query-runs/{run_id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `run_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.query_runs.get(run_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.query_runs.get(run_id="string")

```

#### Response

##### Type
[QueryRun](/sideko_allium/types/models/query_run.py)

##### Example
`{"created_at": "1970-01-01T00:00:00", "creator_id": "string", "query_config": {"limit": 123, "sql": "string"}, "query_id": "string", "run_id": "string", "status": "canceled"}`

### Cancel Query Run <a name="cancel"></a>



**API Endpoint**: `POST /api/v1/explorer/query-runs/{run_id}/cancel`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `run_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.query_runs.cancel(run_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.query_runs.cancel(run_id="string")

```
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

## Submodules
- [error](error/README.md) - error
- [results](results/README.md) - results
- [status](status/README.md) - status

