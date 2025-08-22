# explorer_queries

## Module Functions
### Execute Query <a name="run"></a>



**API Endpoint**: `POST /api/v1/explorer/queries/{query_id}/run`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ |  | `{}` |
| `query_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.queries.run(data={}, query_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.queries.run(data={}, query_id="string")

```

### Execute Query Async <a name="run_async"></a>



**API Endpoint**: `POST /api/v1/explorer/queries/{query_id}/run-async`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `parameters` | ✓ |  | `{}` |
| `query_id` | ✓ |  | `"string"` |
| `run_config` | ✗ |  | `{}` |
| `└─ limit` | ✗ |  | `123` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.queries.run_async(parameters={}, query_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.queries.run_async(parameters={}, query_id="string")

```
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

