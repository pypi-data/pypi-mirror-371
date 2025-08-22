# streams_data_management_filter_data_sources

## Module Functions
### Delete a filter data source <a name="delete"></a>

Delete a filter data source by ID. Will fail if the data source is being used by any filters.

**API Endpoint**: `DELETE /api/v1/streams/data-management/filter-data-sources/{data_source_id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data_source_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.filter_data_sources.delete(data_source_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.filter_data_sources.delete(
    data_source_id="string"
)

```

#### Response

##### Type
[ResponseWithId](/sideko_allium/types/models/response_with_id.py)

##### Example
`{"message": "string"}`

### Filter Data Sources <a name="list"></a>

Get all filter data sources

**API Endpoint**: `GET /api/v1/streams/data-management/filter-data-sources`

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.filter_data_sources.list()

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.filter_data_sources.list()

```

#### Response

##### Type
List of [FilterDataSourceResponse](/sideko_allium/types/models/filter_data_source_response.py)

##### Example
`[{"description": "string", "id": "3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a", "name": "string", "type_": "string"}]`

### Filter Data Source by ID <a name="get"></a>

Get a filter data source by ID

**API Endpoint**: `GET /api/v1/streams/data-management/filter-data-sources/{data_source_id}`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data_source_id` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.filter_data_sources.get(data_source_id="string")

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.filter_data_sources.get(
    data_source_id="string"
)

```

#### Response

##### Type
[FilterDataSourceResponse](/sideko_allium/types/models/filter_data_source_response.py)

##### Example
`{"description": "string", "id": "3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a", "name": "string", "type_": "string"}`

### Filter Data Source <a name="create"></a>

Create a new filter data source by specifying the name and type

**API Endpoint**: `POST /api/v1/streams/data-management/filter-data-sources`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `description` | ✓ |  | `"string"` |
| `name` | ✓ |  | `"string"` |
| `type_` | ✓ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.filter_data_sources.create(
    description="string", name="string", type_="string"
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.filter_data_sources.create(
    description="string", name="string", type_="string"
)

```

#### Response

##### Type
[ResponseWithId](/sideko_allium/types/models/response_with_id.py)

##### Example
`{"message": "string"}`

### Filter Data Source Values <a name="update_values"></a>

Update values for a filter data source

**API Endpoint**: `POST /api/v1/streams/data-management/filter-data-sources/{data_source_id}/values`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data_source_id` | ✓ |  | `"string"` |
| `operation` | ✓ |  | `"ADD"` |
| `values` | ✓ |  | `["string"]` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.streams.data_management.filter_data_sources.update_values(
    data_source_id="string", operation="ADD", values=["string"]
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.streams.data_management.filter_data_sources.update_values(
    data_source_id="string", operation="ADD", values=["string"]
)

```

#### Response

##### Type
[FilterDataSourceValuesResponse](/sideko_allium/types/models/filter_data_source_values_response.py)

##### Example
`{"message": "string"}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

