import pydantic
import typing


class TOrdinalsInscriptionTransfer(pydantic.BaseModel):
    """
    Bitcoin ordinals inscription transfer entity.
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
    content_protocol: typing.Optional[str] = pydantic.Field(
        alias="content_protocol", default=None
    )
    content_type: typing.Optional[str] = pydantic.Field(
        alias="content_type", default=None
    )
    from_address: typing.Optional[str] = pydantic.Field(
        alias="from_address", default=None
    )
    from_utxo_id: typing.Optional[str] = pydantic.Field(
        alias="from_utxo_id", default=None
    )
    from_utxo_offset: typing.Optional[int] = pydantic.Field(
        alias="from_utxo_offset", default=None
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
    output_index: typing.Optional[int] = pydantic.Field(
        alias="output_index", default=None
    )
    parsed_content: typing.Optional[str] = pydantic.Field(
        alias="parsed_content", default=None
    )
    sat_tx_offset: typing.Optional[int] = pydantic.Field(
        alias="sat_tx_offset", default=None
    )
    sent_as_fee: typing.Optional[bool] = pydantic.Field(
        alias="sent_as_fee", default=None
    )
    to_address: typing.Optional[str] = pydantic.Field(alias="to_address", default=None)
    to_utxo_id: typing.Optional[str] = pydantic.Field(alias="to_utxo_id", default=None)
    to_utxo_offset: typing.Optional[int] = pydantic.Field(
        alias="to_utxo_offset", default=None
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
    transfer_count: typing.Optional[int] = pydantic.Field(
        alias="transfer_count", default=None
    )
    value: typing.Optional[str] = pydantic.Field(alias="value", default=None)
