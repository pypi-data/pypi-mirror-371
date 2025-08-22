import pydantic
import typing


class TOrdinalsTokenTransfer(pydantic.BaseModel):
    """
    Bitcoin ordinals token transfer entity.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Any]

    amount: typing.Optional[str] = pydantic.Field(alias="amount", default=None)
    block_hash: typing.Optional[str] = pydantic.Field(alias="block_hash", default=None)
    block_number: typing.Optional[int] = pydantic.Field(
        alias="block_number", default=None
    )
    block_timestamp: typing.Optional[str] = pydantic.Field(
        alias="block_timestamp", default=None
    )
    deployment_id: typing.Optional[str] = pydantic.Field(
        alias="deployment_id", default=None
    )
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
    from_address: typing.Optional[str] = pydantic.Field(
        alias="from_address", default=None
    )
    from_available_balance_post: typing.Optional[str] = pydantic.Field(
        alias="from_available_balance_post", default=None
    )
    from_available_balance_pre: typing.Optional[str] = pydantic.Field(
        alias="from_available_balance_pre", default=None
    )
    from_overall_balance_post: typing.Optional[str] = pydantic.Field(
        alias="from_overall_balance_post", default=None
    )
    from_overall_balance_pre: typing.Optional[str] = pydantic.Field(
        alias="from_overall_balance_pre", default=None
    )
    inscription_id: str = pydantic.Field(
        alias="inscription_id",
    )
    is_valid: typing.Optional[bool] = pydantic.Field(alias="is_valid", default=None)
    pseudo_offset_order: typing.Optional[int] = pydantic.Field(
        alias="pseudo_offset_order", default=None
    )
    sat_tx_offset: typing.Optional[int] = pydantic.Field(
        alias="sat_tx_offset", default=None
    )
    to_address: typing.Optional[str] = pydantic.Field(alias="to_address", default=None)
    to_available_balance_post: typing.Optional[str] = pydantic.Field(
        alias="to_available_balance_post", default=None
    )
    to_available_balance_pre: typing.Optional[str] = pydantic.Field(
        alias="to_available_balance_pre", default=None
    )
    to_overall_balance_post: typing.Optional[str] = pydantic.Field(
        alias="to_overall_balance_post", default=None
    )
    to_overall_balance_pre: typing.Optional[str] = pydantic.Field(
        alias="to_overall_balance_pre", default=None
    )
    token_amt: typing.Optional[str] = pydantic.Field(alias="token_amt", default=None)
    token_dec: typing.Optional[int] = pydantic.Field(alias="token_dec", default=None)
    token_lim: typing.Optional[str] = pydantic.Field(alias="token_lim", default=None)
    token_max: typing.Optional[str] = pydantic.Field(alias="token_max", default=None)
    token_minted: typing.Optional[str] = pydantic.Field(
        alias="token_minted", default=None
    )
    token_op: typing.Optional[str] = pydantic.Field(alias="token_op", default=None)
    token_tick: typing.Optional[str] = pydantic.Field(alias="token_tick", default=None)
    token_transfer_type: typing.Optional[str] = pydantic.Field(
        alias="token_transfer_type", default=None
    )
    token_type: typing.Optional[str] = pydantic.Field(alias="token_type", default=None)
    transaction_hash: typing.Optional[str] = pydantic.Field(
        alias="transaction_hash", default=None
    )
    transaction_index: typing.Optional[int] = pydantic.Field(
        alias="transaction_index", default=None
    )
