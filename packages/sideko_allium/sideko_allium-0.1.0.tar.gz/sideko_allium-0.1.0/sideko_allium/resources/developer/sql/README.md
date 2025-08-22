# developer_sql

## Module Functions
### Raw Sql Query <a name="query"></a>



**API Endpoint**: `POST /api/v1/developer/{chain}/sql/`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `chain` | ✓ |  | `"abstract"` |
| `query` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.sql.query(chain="abstract", query="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.sql.query(chain="abstract", query="string")

```
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

