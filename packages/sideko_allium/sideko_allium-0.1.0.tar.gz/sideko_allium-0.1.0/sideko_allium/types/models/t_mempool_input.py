import pydantic
import typing


class TMempoolInput(pydantic.BaseModel):
    """
    Bitcoin mempool input entity.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Any]

    block_hash: typing.Optional[str] = pydantic.Field(alias="block_hash", default=None)
    block_timestamp: typing.Optional[str] = pydantic.Field(
        alias="block_timestamp", default=None
    )
    fetched_at: typing.Optional[str] = pydantic.Field(alias="fetched_at", default=None)
    index: typing.Optional[int] = pydantic.Field(alias="index", default=None)
    input_id: str = pydantic.Field(
        alias="input_id",
    )
    script_asm: typing.Optional[str] = pydantic.Field(alias="script_asm", default=None)
    script_hex: typing.Optional[str] = pydantic.Field(alias="script_hex", default=None)
    sequence: typing.Optional[int] = pydantic.Field(alias="sequence", default=None)
    spent_output_index: typing.Optional[int] = pydantic.Field(
        alias="spent_output_index", default=None
    )
    spent_transaction_hash: typing.Optional[str] = pydantic.Field(
        alias="spent_transaction_hash", default=None
    )
    spent_utxo_id: typing.Optional[str] = pydantic.Field(
        alias="spent_utxo_id", default=None
    )
    transaction_hash: typing.Optional[str] = pydantic.Field(
        alias="transaction_hash", default=None
    )
    txinwitness: typing.Optional[
        typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Any]]
    ] = pydantic.Field(alias="txinwitness", default=None)
