# developer_prices

## Module Functions
### Get Latest Prices <a name="list"></a>

Get the latest prices for the given token addresses.
Returns price information including timestamp, price, open, high, close, low, and volume.
Args:
    payloads: List of PayloadTokenAddress objects containing token addresses and chains
Returns:
    Dictionary mapping chain types to lists of PayloadTokenAddress objects
Example:
    ```
    [
        {
            "token_address": "1Qf8gESP4i6CFNWerUSDdLKJ9U1LpqTYvjJ2MM4pain",
            "chain": "solana"
        }
    ]
    ```

**API Endpoint**: `POST /api/v1/developer/prices`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ |  | `[{"chain": "string", "token_address": "string"}]` |
| `with_liquidity_info` | ✗ | If true, returns total_liquidity_usd as well. See https://docs.allium.so/developer/data-tips#token-liquidity for more details. | `True` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.prices.list(
    data=[{"chain": "string", "token_address": "string"}]
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.prices.list(
    data=[{"chain": "string", "token_address": "string"}]
)

```

#### Response

##### Type
[EnvelopeTokenPriceV2_](/sideko_allium/types/models/envelope_token_price_v2_.py)

##### Example
`{"items": [{"address": "string", "attributes": {}, "chain": "string", "close": 123.0, "high": 123.0, "low": 123.0, "open": 123.0, "price": 123.0, "timestamp": "1970-01-01T00:00:00"}]}`

### Get Prices At Timestamp <a name="list_at_timestamp"></a>

Get the price for a list of token addresses at a given timestamp.
If a token doesn't have a price at the given timestamp (because there weren't any trades at that time),
the price will be the price at the closest timestamp before the given timestamp.
Use 'stalesness_tolerance' to specify the max lookback time (in minutes) for a price.
Args:
    payloads: PayloadTokenAddressAtTimestamp objects containing timestamp, granularity, stalesness_tolerance and a list of token address + chain pairs.
Returns:
    Dictionary mapping chain types to lists of PayloadTokenAddressAtTimestamp objects
Example:
    ```
    [
        {
            "addresses": [
                {
                    "token_address": "1Qf8gESP4i6CFNWerUSDdLKJ9U1LpqTYvjJ2MM4pain",
                    "chain": "solana"
                }
            ],
            "timestamp": "2025-07-11T00:00:00Z",
            "time_granularity": "5m",
            "staleness_tolerance": 120
        }
    ]
    ```

**API Endpoint**: `POST /api/v1/developer/prices/at-timestamp`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `addresses` | ✓ |  | `[{"chain": "string", "token_address": "string"}]` |
| `time_granularity` | ✓ |  | `"15s"` |
| `timestamp` | ✓ |  | `"1970-01-01T00:00:00"` |
| `staleness_tolerance` | ✗ |  | `"string"` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.prices.list_at_timestamp(
    addresses=[
        {"chain": "string", "token_address": "string"},
        {"chain": "string", "token_address": "string"},
    ],
    time_granularity="5m",
    timestamp="2025-03-07T00:00:00Z",
    staleness_tolerance="1h",
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.prices.list_at_timestamp(
    addresses=[
        {"chain": "string", "token_address": "string"},
        {"chain": "string", "token_address": "string"},
    ],
    time_granularity="5m",
    timestamp="2025-03-07T00:00:00Z",
    staleness_tolerance="1h",
)

```

#### Response

##### Type
[EnvelopeTokenPriceAtTimestamp_](/sideko_allium/types/models/envelope_token_price_at_timestamp_.py)

##### Example
`{"items": [{"chain": "string", "input_timestamp": "1970-01-01T00:00:00", "mint": "string", "price": 123.0, "price_timestamp": "1970-01-01T00:00:00"}]}`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

## Submodules
- [history](history/README.md) - history
- [stats](stats/README.md) - stats

