# supported_chains_realtime_apis

## Module Functions
### Get Supported Endpoints <a name="get_endpoints"></a>



**API Endpoint**: `GET /api/v1/supported-chains/realtime-apis`

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.supported_chains.realtime_apis.get_endpoints()

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.supported_chains.realtime_apis.get_endpoints()

```

### Get Supported Chains <a name="get_chains"></a>



**API Endpoint**: `POST /api/v1/supported-chains/realtime-apis`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `endpoints` | ✓ |  | `["custom_sql"]` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.supported_chains.realtime_apis.get_chains(endpoints=["custom_sql"])

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.supported_chains.realtime_apis.get_chains(endpoints=["custom_sql"])

```
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

