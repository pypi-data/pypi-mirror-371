# streams_data_management_workflows

## Module Functions
### Delete a workflow <a name="delete"></a>

Delete a workflow by ID

**API Endpoint**: `DELETE /api/v1/streams/data-management/workflows/{id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.workflows.delete(id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.workflows.delete(id="string")

```

#### Response

##### Type
[DeleteDataTransformationWorkflowResponse](/sideko_allium/types/models/delete_data_transformation_workflow_response.py)

##### Example
`{"message": "string"}`

### Workflows <a name="list"></a>

Get all workflows

**API Endpoint**: `GET /api/v1/streams/data-management/workflows`

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.workflows.list()

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.workflows.list()

```

#### Response

##### Type
List of [DataTransformationWorkflowResponse](/sideko_allium/types/models/data_transformation_workflow_response.py)

##### Example
`[{"data_destination_config": {}, "data_source_config": {"topic": "string"}, "filter_id": "3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a"}]`

### Workflow by ID <a name="get"></a>

Get a workflow by ID

**API Endpoint**: `GET /api/v1/streams/data-management/workflows/{id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.workflows.get(id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.workflows.get(id="string")

```

#### Response

##### Type
[DataTransformationWorkflowResponse](/sideko_allium/types/models/data_transformation_workflow_response.py)

##### Example
`{"data_destination_config": {}, "data_source_config": {"topic": "string"}, "filter_id": "3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a"}`

### Workflow <a name="create"></a>

Create a new workflow by specifying the description, filter, data source, and data destination

**API Endpoint**: `POST /api/v1/streams/data-management/workflows`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data_destination_config` | ✓ |  | `{}` |
| `data_source_config` | ✓ |  | `{"topic": "string"}` |
| `└─ topic` | ✓ |  | `"string"` |
| `└─ type_` | ✗ |  | `"string"` |
| `filter_id` | ✓ |  | `"3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a"` |
| `description` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.workflows.create(
    data_destination_config={},
    data_source_config={"topic": "string"},
    filter_id="3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a",
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.workflows.create(
    data_destination_config={},
    data_source_config={"topic": "string"},
    filter_id="3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a",
)

```

#### Response

##### Type
[DataTransformationWorkflowResponse](/sideko_allium/types/models/data_transformation_workflow_response.py)

##### Example
`{"data_destination_config": {}, "data_source_config": {"topic": "string"}, "filter_id": "3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a"}`

### Update a workflow <a name="update"></a>

Update a workflow by ID

**API Endpoint**: `PUT /api/v1/streams/data-management/workflows/{id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `filter_id` | ✓ |  | `"3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a"` |
| `id` | ✓ |  | `"string"` |
| `description` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.workflows.update(
    filter_id="3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a", id="string"
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.workflows.update(
    filter_id="3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a", id="string"
)

```

#### Response

##### Type
[DataTransformationWorkflowResponse](/sideko_allium/types/models/data_transformation_workflow_response.py)

##### Example
`{"data_destination_config": {}, "data_source_config": {"topic": "string"}, "filter_id": "3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a"}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

