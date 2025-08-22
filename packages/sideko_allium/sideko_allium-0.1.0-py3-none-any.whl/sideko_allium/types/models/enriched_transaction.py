import pydantic
import typing


class EnrichedTransaction(pydantic.BaseModel):
    """
    EnrichedTransaction
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    action: typing.Optional[str] = pydantic.Field(alias="action", default=None)
    block_hash: str = pydantic.Field(
        alias="block_hash",
    )
    block_number: int = pydantic.Field(
        alias="block_number",
    )
    block_timestamp: str = pydantic.Field(
        alias="block_timestamp",
    )
    from_address: str = pydantic.Field(
        alias="from_address",
    )
    function_signature: typing.Optional[str] = pydantic.Field(
        alias="function_signature", default=None
    )
    gas: typing.Optional[int] = pydantic.Field(alias="gas", default=None)
    gas_price: typing.Optional[int] = pydantic.Field(alias="gas_price", default=None)
    hash: str = pydantic.Field(
        alias="hash",
    )
    input: typing.Optional[str] = pydantic.Field(alias="input", default=None)
    max_fee_per_gas: typing.Optional[int] = pydantic.Field(
        alias="max_fee_per_gas", default=None
    )
    max_priority_fee_per_gas: typing.Optional[int] = pydantic.Field(
        alias="max_priority_fee_per_gas", default=None
    )
    nonce: int = pydantic.Field(
        alias="nonce",
    )
    receipt_contract_address: typing.Optional[str] = pydantic.Field(
        alias="receipt_contract_address", default=None
    )
    receipt_cumulative_gas_used: typing.Optional[int] = pydantic.Field(
        alias="receipt_cumulative_gas_used", default=None
    )
    receipt_effective_gas_price: typing.Optional[int] = pydantic.Field(
        alias="receipt_effective_gas_price", default=None
    )
    receipt_gas_used: typing.Optional[int] = pydantic.Field(
        alias="receipt_gas_used", default=None
    )
    receipt_root: typing.Optional[str] = pydantic.Field(
        alias="receipt_root", default=None
    )
    receipt_status: typing.Optional[int] = pydantic.Field(
        alias="receipt_status", default=None
    )
    to_address: typing.Optional[str] = pydantic.Field(alias="to_address", default=None)
    transaction_index: int = pydantic.Field(
        alias="transaction_index",
    )
    transaction_type: typing.Optional[int] = pydantic.Field(
        alias="transaction_type", default=None
    )
    value: str = pydantic.Field(
        alias="value",
    )
