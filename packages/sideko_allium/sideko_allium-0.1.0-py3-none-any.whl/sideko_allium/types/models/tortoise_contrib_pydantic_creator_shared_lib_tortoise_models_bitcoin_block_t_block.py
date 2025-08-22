import pydantic
import typing


class TortoiseContribPydanticCreatorSharedLibTortoiseModelsBitcoinBlockTBlock(
    pydantic.BaseModel
):
    """
    Bitcoin block entity.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Any]

    bits: typing.Optional[str] = pydantic.Field(alias="bits", default=None)
    chainwork: typing.Optional[str] = pydantic.Field(alias="chainwork", default=None)
    confirmations: typing.Optional[int] = pydantic.Field(
        alias="confirmations", default=None
    )
    difficulty: typing.Optional[str] = pydantic.Field(alias="difficulty", default=None)
    fetched_at: typing.Optional[str] = pydantic.Field(alias="fetched_at", default=None)
    hash: str = pydantic.Field(
        alias="hash",
    )
    is_reorg: typing.Optional[bool] = pydantic.Field(alias="is_reorg", default=None)
    median_time: typing.Optional[int] = pydantic.Field(
        alias="median_time", default=None
    )
    merkle_root: typing.Optional[str] = pydantic.Field(
        alias="merkle_root", default=None
    )
    next_blockhash: typing.Optional[str] = pydantic.Field(
        alias="next_blockhash", default=None
    )
    nonce: typing.Optional[str] = pydantic.Field(alias="nonce", default=None)
    number: typing.Optional[int] = pydantic.Field(alias="number", default=None)
    previous_blockhash: typing.Optional[str] = pydantic.Field(
        alias="previous_blockhash", default=None
    )
    size: typing.Optional[int] = pydantic.Field(alias="size", default=None)
    stripped_size: typing.Optional[int] = pydantic.Field(
        alias="stripped_size", default=None
    )
    timestamp: typing.Optional[str] = pydantic.Field(alias="timestamp", default=None)
    transaction_count: typing.Optional[int] = pydantic.Field(
        alias="transaction_count", default=None
    )
    version: typing.Optional[int] = pydantic.Field(alias="version", default=None)
    weight: typing.Optional[int] = pydantic.Field(alias="weight", default=None)
