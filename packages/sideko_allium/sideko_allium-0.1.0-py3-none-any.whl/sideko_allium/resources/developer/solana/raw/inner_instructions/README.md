# developer_solana_raw_inner_instructions

## Module Functions
### Get Inner Instructions <a name="get"></a>



**API Endpoint**: `POST /api/v1/developer/solana/raw/inner_instructions`

#### Parameters

| Parameter | Required | Description | Example |
|-----------|:--------:|-------------|--------|
| `data` | ✓ |  | `[{"block_timestamp": "1970-01-01T00:00:00", "txn_id": "string"}]` |

#### Synchronous Client

```python
from os import getenv
from sideko_allium import Client

client = Client(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = client.developer.solana.raw.inner_instructions.get(
    data=[{"block_timestamp": "1970-01-01T00:00:00", "txn_id": "string"}]
)

```

#### Asynchronous Client

```python
from os import getenv
from sideko_allium import AsyncClient

client = AsyncClient(key=getenv("API_KEY"), token=getenv("API_TOKEN"))
res = await client.developer.solana.raw.inner_instructions.get(
    data=[{"block_timestamp": "1970-01-01T00:00:00", "txn_id": "string"}]
)

```

#### Response

##### Type
List of [InnerInstruction](/sideko_allium/types/models/inner_instruction.py)

##### Example
`[{"accounts": ["string"], "data": "string", "data_hex": "string", "inner_instruction_index": 123, "instruction_index": 123, "is_voting": True, "parent_instruction_program_id": "string", "parent_tx_signer": "string", "parent_tx_success": True, "parsed": "string", "parsed_type": "string", "program_id": "string", "program_name": "string", "txn_id": "string", "txn_index": 123}]`
<!-- CUSTOM DOCS START -->

<!-- CUSTOM DOCS END -->

