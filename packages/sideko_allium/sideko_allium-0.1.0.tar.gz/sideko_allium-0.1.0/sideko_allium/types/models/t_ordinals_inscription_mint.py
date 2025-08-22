import pydantic
import typing


class TOrdinalsInscriptionMint(pydantic.BaseModel):
    """
    Bitcoin ordinals inscription mint entity.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Any]

    block_hash: typing.Optional[str] = pydantic.Field(alias="block_hash", default=None)
    block_number: typing.Optional[int] = pydantic.Field(
        alias="block_number", default=None
    )
    block_timestamp: typing.Optional[str] = pydantic.Field(
        alias="block_timestamp", default=None
    )
    cleaned_token_tick: typing.Optional[str] = pydantic.Field(
        alias="cleaned_token_tick", default=None
    )
    cleaned_token_type: typing.Optional[str] = pydantic.Field(
        alias="cleaned_token_type", default=None
    )
    content_length: typing.Optional[int] = pydantic.Field(
        alias="content_length", default=None
    )
    content_protocol: typing.Optional[str] = pydantic.Field(
        alias="content_protocol", default=None
    )
    content_type: typing.Optional[str] = pydantic.Field(
        alias="content_type", default=None
    )
    genesis_fee: typing.Optional[int] = pydantic.Field(
        alias="genesis_fee", default=None
    )
    input_address0: typing.Optional[str] = pydantic.Field(
        alias="input_address0", default=None
    )
    input_index: typing.Optional[int] = pydantic.Field(
        alias="input_index", default=None
    )
    inscription_id: str = pydantic.Field(
        alias="inscription_id",
    )
    is_token: typing.Optional[bool] = pydantic.Field(alias="is_token", default=None)
    is_unstable: typing.Optional[bool] = pydantic.Field(
        alias="is_unstable", default=None
    )
    is_unstable_remarks: typing.Optional[str] = pydantic.Field(
        alias="is_unstable_remarks", default=None
    )
    output_address: typing.Optional[str] = pydantic.Field(
        alias="output_address", default=None
    )
    output_index: typing.Optional[int] = pydantic.Field(
        alias="output_index", default=None
    )
    output_offset: typing.Optional[int] = pydantic.Field(
        alias="output_offset", default=None
    )
    output_utxo_id: typing.Optional[str] = pydantic.Field(
        alias="output_utxo_id", default=None
    )
    parsed_content: typing.Optional[str] = pydantic.Field(
        alias="parsed_content", default=None
    )
    parsed_witness: typing.Optional[
        typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Any]]
    ] = pydantic.Field(alias="parsed_witness", default=None)
    sat_tx_offset: typing.Optional[int] = pydantic.Field(
        alias="sat_tx_offset", default=None
    )
    sent_as_fee: typing.Optional[bool] = pydantic.Field(
        alias="sent_as_fee", default=None
    )
    spent_output_index: typing.Optional[int] = pydantic.Field(
        alias="spent_output_index", default=None
    )
    spent_transaction_hash: typing.Optional[str] = pydantic.Field(
        alias="spent_transaction_hash", default=None
    )
    spent_utxo_id: typing.Optional[str] = pydantic.Field(
        alias="spent_utxo_id", default=None
    )
    token_amt: typing.Optional[str] = pydantic.Field(alias="token_amt", default=None)
    token_op: typing.Optional[str] = pydantic.Field(alias="token_op", default=None)
    token_tick: typing.Optional[str] = pydantic.Field(alias="token_tick", default=None)
    transaction_hash: typing.Optional[str] = pydantic.Field(
        alias="transaction_hash", default=None
    )
    transaction_index: typing.Optional[int] = pydantic.Field(
        alias="transaction_index", default=None
    )
    value: typing.Optional[str] = pydantic.Field(alias="value", default=None)
