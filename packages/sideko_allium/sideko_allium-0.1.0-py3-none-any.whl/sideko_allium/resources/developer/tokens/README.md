# developer_tokens

## Module Functions
### Get Tokens <a name="list"></a>



**API Endpoint**: `POST /api/v1/developer/tokens`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ |  | `[{"chain": "string", "token_address": "string"}]` |
| `with_liquidity_info` | ✗ | If true, returns total_liquidity_usd. See https://docs.allium.so/developer/data-tips#token-liquidity for more details. | `True` |
| `with_price_info` | ✗ | If true, returns price data. | `True` |
| `with_supply_info` | ✗ | If true, returns total supply. | `True` |
| `with_volume` | ✗ | If true, returns 1h and 24h volume data. | `True` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.tokens.list(
    data=[{"chain": "string", "token_address": "string"}]
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.tokens.list(
    data=[{"chain": "string", "token_address": "string"}]
)

```

#### Response

##### Type
List of [Token](/sideko_allium/types/models/token.py)

##### Example
`[{"address": "string", "chain": "string", "type_": "evm_erc1155"}]`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

