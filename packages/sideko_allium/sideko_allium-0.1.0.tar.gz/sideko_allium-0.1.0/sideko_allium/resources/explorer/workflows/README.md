# explorer_workflows

## Module Functions
### Run Workflow <a name="run"></a>



**API Endpoint**: `POST /api/v1/explorer/workflows/{workflow_id}/run`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `workflow_id` | ✓ |  | `"string"` |
| `variables` | ✗ |  | `{}` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.explorer.workflows.run(workflow_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.explorer.workflows.run(workflow_id="string")

```
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

