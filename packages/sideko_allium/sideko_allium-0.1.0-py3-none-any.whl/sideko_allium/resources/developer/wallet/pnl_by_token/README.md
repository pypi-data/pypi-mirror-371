# developer_wallet_pnl_by_token

## Module Functions
### Get Pnl By Token <a name="get"></a>



**API Endpoint**: `POST /api/v1/developer/wallet/pnl-by-token`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ |  | `[{"address": "string", "chain": "string", "token_address": "string"}]` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.wallet.pnl_by_token.get(
    data=[{"address": "string", "chain": "string", "token_address": "string"}]
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.wallet.pnl_by_token.get(
    data=[{"address": "string", "chain": "string", "token_address": "string"}]
)

```

#### Response

##### Type
[ResponseEnvelopeUnionPnlByTokenNoneType_](/sideko_allium/types/models/response_envelope_union_pnl_by_token_none_type_.py)

##### Example
`{}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

## Submodules
- [history](history/README.md) - history

