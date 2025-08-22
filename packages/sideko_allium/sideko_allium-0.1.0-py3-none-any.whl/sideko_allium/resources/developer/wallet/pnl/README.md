# developer_wallet_pnl

## Module Functions
### Get Pnl <a name="get"></a>



**API Endpoint**: `POST /api/v1/developer/wallet/pnl`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ |  | `[{"address": "string", "chain": "string"}]` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.wallet.pnl.get(data=[{"address": "string", "chain": "string"}])

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.wallet.pnl.get(
    data=[{"address": "string", "chain": "string"}]
)

```

#### Response

##### Type
[ResponseEnvelopePnlByWallet_](/sideko_allium/types/models/response_envelope_pnl_by_wallet_.py)

##### Example
`{}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

## Submodules
- [history](history/README.md) - history

