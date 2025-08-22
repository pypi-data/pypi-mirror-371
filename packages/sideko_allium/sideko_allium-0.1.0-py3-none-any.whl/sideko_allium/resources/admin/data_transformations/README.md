# admin_data_transformations

## Module Functions
### Admin refresh a workflow <a name="refresh"></a>

Admin endpoint to refresh a workflow by org_id and workflow_id

**API Endpoint**: `POST /admin/data-transformations/refresh`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `org_id` | ✓ |  | `"string"` |
| `workflow_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.admin.data_transformations.refresh(org_id="string", workflow_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.admin.data_transformations.refresh(
    org_id="string", workflow_id="string"
)

```

#### Response

##### Type
[AdminRefreshWorkflowResponse](/sideko_allium/types/models/admin_refresh_workflow_response.py)

##### Example
`{"message": "string"}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

