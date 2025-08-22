import pydantic
import typing


class TortoiseContribPydanticCreatorSharedLibTortoiseModelsEvmBlockTBlock(
    pydantic.BaseModel
):
    """
    EVM block entity.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Any]

    base_fee_per_gas: typing.Optional[int] = pydantic.Field(
        alias="base_fee_per_gas", default=None
    )
    difficulty: typing.Optional[str] = pydantic.Field(alias="difficulty", default=None)
    extra_data: typing.Optional[str] = pydantic.Field(alias="extra_data", default=None)
    gas_limit: typing.Optional[int] = pydantic.Field(alias="gas_limit", default=None)
    gas_used: typing.Optional[int] = pydantic.Field(alias="gas_used", default=None)
    hash: str = pydantic.Field(
        alias="hash",
    )
    logs_bloom: typing.Optional[str] = pydantic.Field(alias="logs_bloom", default=None)
    miner: typing.Optional[str] = pydantic.Field(alias="miner", default=None)
    nonce: typing.Optional[str] = pydantic.Field(alias="nonce", default=None)
    number: typing.Optional[int] = pydantic.Field(alias="number", default=None)
    parent_hash: typing.Optional[str] = pydantic.Field(
        alias="parent_hash", default=None
    )
    receipts_root: typing.Optional[str] = pydantic.Field(
        alias="receipts_root", default=None
    )
    sha3_uncles: typing.Optional[str] = pydantic.Field(
        alias="sha3_uncles", default=None
    )
    size: typing.Optional[int] = pydantic.Field(alias="size", default=None)
    state_root: str = pydantic.Field(
        alias="state_root",
    )
    timestamp: typing.Optional[str] = pydantic.Field(alias="timestamp", default=None)
    total_difficulty: typing.Optional[str] = pydantic.Field(
        alias="total_difficulty", default=None
    )
    transaction_count: typing.Optional[int] = pydantic.Field(
        alias="transaction_count", default=None
    )
    transactions_root: typing.Optional[str] = pydantic.Field(
        alias="transactions_root", default=None
    )
