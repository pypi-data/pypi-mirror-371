# streams_data_management_filters

## Module Functions
### Delete a filter <a name="delete"></a>

Delete a filter by ID

**API Endpoint**: `DELETE /api/v1/streams/data-management/filters/{id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.filters.delete(id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.filters.delete(id="string")

```

#### Response

##### Type
[ResponseWithId](/sideko_allium/types/models/response_with_id.py)

##### Example
`{"message": "string"}`

### Filters <a name="list"></a>

Get all filters

**API Endpoint**: `GET /api/v1/streams/data-management/filters`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `id` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.filters.list()

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.filters.list()

```

### Filter by ID <a name="get"></a>

Get a filter by ID

**API Endpoint**: `GET /api/v1/streams/data-management/filters/{id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.filters.get(id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.filters.get(id="string")

```

### Filter <a name="create"></a>

Create a new filter by specifying the field, operator and type

**API Endpoint**: `POST /api/v1/streams/data-management/filters`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `filter` | ✓ |  | `{}` |
| `id` | ✗ |  | `"3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a"` |
| `organization_id` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.filters.create(filter={})

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.filters.create(filter={})

```

#### Response

##### Type
[ResponseWithId](/sideko_allium/types/models/response_with_id.py)

##### Example
`{"message": "string"}`

### Update a filter <a name="update"></a>

Update a filter by ID

**API Endpoint**: `PUT /api/v1/streams/data-management/filters/{id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `filter` | ✓ |  | `{}` |
| `id_path` | ✓ |  | `"string"` |
| `id` | ✗ |  | `"3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a"` |
| `organization_id` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.filters.update(filter={}, id_path="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.filters.update(filter={}, id_path="string")

```

#### Response

##### Type
[ResponseWithId](/sideko_allium/types/models/response_with_id.py)

##### Example
`{"message": "string"}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

