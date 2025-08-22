# explorer_query_runs_results

## Module Functions
### Get Query Run Results <a name="list"></a>



**API Endpoint**: `GET /api/v1/explorer/query-runs/{run_id}/results`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `run_id` | ✓ |  | `"string"` |
| `f` | ✗ |  | `"csv"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.query_runs.results.list(run_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.query_runs.results.list(run_id="string")

```

#### Response

##### Type
[QueryResult](/sideko_allium/types/models/query_result.py)

##### Example
`{"meta": {"columns": [{"data_type": "string", "name": "string"}]}, "sql": "string"}`

### Get Query Run Results With Ssa <a name="get"></a>



**API Endpoint**: `POST /api/v1/explorer/query-runs/{run_id}/results`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `run_id` | ✓ |  | `"string"` |
| `config` | ✗ |  | `{}` |
| `└─ columns` | ✗ |  | `[{"name": "string"}]` |
| `└─ dataframe_name` | ✗ |  | `"string"` |
| `└─ filters` | ✗ |  | `[]` |
| `└─ limit` | ✗ |  | `123` |
| `└─ offset` | ✗ |  | `123` |
| `└─ order` | ✗ |  | `[{"direction": "asc", "name": "string"}]` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.query_runs.results.get(run_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.query_runs.results.get(run_id="string")

```

#### Response

##### Type
[QueryResult](/sideko_allium/types/models/query_result.py)

##### Example
`{"meta": {"columns": [{"data_type": "string", "name": "string"}]}, "sql": "string"}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

