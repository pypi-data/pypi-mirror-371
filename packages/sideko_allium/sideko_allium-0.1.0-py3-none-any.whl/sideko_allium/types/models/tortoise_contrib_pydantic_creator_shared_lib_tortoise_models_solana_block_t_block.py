import pydantic
import typing


class TortoiseContribPydanticCreatorSharedLibTortoiseModelsSolanaBlockTBlock(
    pydantic.BaseModel
):
    """
    Represents a row in the solana.blocks table.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Any]

    hash: typing.Optional[str] = pydantic.Field(alias="hash", default=None)
    height: typing.Optional[int] = pydantic.Field(alias="height", default=None)
    nonvoting_transaction_count: typing.Optional[int] = pydantic.Field(
        alias="nonvoting_transaction_count", default=None
    )
    parent_slot: typing.Optional[int] = pydantic.Field(
        alias="parent_slot", default=None
    )
    previous_block_hash: typing.Optional[str] = pydantic.Field(
        alias="previous_block_hash", default=None
    )
    reward_count: typing.Optional[int] = pydantic.Field(
        alias="reward_count", default=None
    )
    slot: int = pydantic.Field(
        alias="slot",
    )
    timestamp: typing.Optional[str] = pydantic.Field(alias="timestamp", default=None)
    transaction_count: typing.Optional[int] = pydantic.Field(
        alias="transaction_count", default=None
    )
