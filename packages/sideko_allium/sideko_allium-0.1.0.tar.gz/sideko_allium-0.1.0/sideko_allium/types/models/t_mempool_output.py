import pydantic
import typing


class TMempoolOutput(pydantic.BaseModel):
    """
    Bitcoin mempool output entity.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Any]

    address: typing.Optional[str] = pydantic.Field(alias="address", default=None)
    address0: typing.Optional[str] = pydantic.Field(alias="address0", default=None)
    addresses: typing.Optional[str] = pydantic.Field(alias="addresses", default=None)
    block_hash: typing.Optional[str] = pydantic.Field(alias="block_hash", default=None)
    block_timestamp: typing.Optional[str] = pydantic.Field(
        alias="block_timestamp", default=None
    )
    description: typing.Optional[str] = pydantic.Field(
        alias="description", default=None
    )
    fetched_at: typing.Optional[str] = pydantic.Field(alias="fetched_at", default=None)
    index: typing.Optional[int] = pydantic.Field(alias="index", default=None)
    script_asm: typing.Optional[str] = pydantic.Field(alias="script_asm", default=None)
    script_hex: typing.Optional[str] = pydantic.Field(alias="script_hex", default=None)
    transaction_hash: typing.Optional[str] = pydantic.Field(
        alias="transaction_hash", default=None
    )
    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
    utxo_id: str = pydantic.Field(
        alias="utxo_id",
    )
    value: typing.Optional[str] = pydantic.Field(alias="value", default=None)
    value_max_exclusive: typing.Optional[str] = pydantic.Field(
        alias="value_max_exclusive", default=None
    )
    value_min_inclusive: typing.Optional[str] = pydantic.Field(
        alias="value_min_inclusive", default=None
    )
