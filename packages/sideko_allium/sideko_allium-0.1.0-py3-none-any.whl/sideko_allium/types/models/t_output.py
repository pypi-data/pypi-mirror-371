import pydantic
import typing


class TOutput(pydantic.BaseModel):
    """
    Bitcoin output entity.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Any]

    address: str = pydantic.Field(
        alias="address",
    )
    address0: str = pydantic.Field(
        alias="address0",
    )
    addresses: str = pydantic.Field(
        alias="addresses",
    )
    block_hash: str = pydantic.Field(
        alias="block_hash",
    )
    block_number: int = pydantic.Field(
        alias="block_number",
    )
    block_timestamp: str = pydantic.Field(
        alias="block_timestamp",
    )
    description: str = pydantic.Field(
        alias="description",
    )
    fetched_at: str = pydantic.Field(
        alias="fetched_at",
    )
    index: int = pydantic.Field(
        alias="index",
    )
    is_patched_block: bool = pydantic.Field(
        alias="is_patched_block",
    )
    is_reorg: bool = pydantic.Field(
        alias="is_reorg",
    )
    script_asm: str = pydantic.Field(
        alias="script_asm",
    )
    script_hex: str = pydantic.Field(
        alias="script_hex",
    )
    transaction_hash: str = pydantic.Field(
        alias="transaction_hash",
    )
    transaction_index: int = pydantic.Field(
        alias="transaction_index",
    )
    type_: str = pydantic.Field(
        alias="type",
    )
    utxo_id: str = pydantic.Field(
        alias="utxo_id",
    )
    value: str = pydantic.Field(
        alias="value",
    )
    value_max_exclusive: str = pydantic.Field(
        alias="value_max_exclusive",
    )
    value_min_inclusive: str = pydantic.Field(
        alias="value_min_inclusive",
    )
