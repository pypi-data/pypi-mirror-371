import pydantic
import typing


class TTransaction(pydantic.BaseModel):
    """
    Bitcoin transaction entity.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Any]

    block_hash: str = pydantic.Field(
        alias="block_hash",
    )
    block_number: int = pydantic.Field(
        alias="block_number",
    )
    block_timestamp: str = pydantic.Field(
        alias="block_timestamp",
    )
    fee: float = pydantic.Field(
        alias="fee",
    )
    fetched_at: typing.Optional[str] = pydantic.Field(alias="fetched_at", default=None)
    hash: str = pydantic.Field(
        alias="hash",
    )
    index: int = pydantic.Field(
        alias="index",
    )
    input_count: int = pydantic.Field(
        alias="input_count",
    )
    is_coinbase: bool = pydantic.Field(
        alias="is_coinbase",
    )
    is_patched_block: typing.Optional[bool] = pydantic.Field(
        alias="is_patched_block", default=None
    )
    is_reorg: typing.Optional[bool] = pydantic.Field(alias="is_reorg", default=None)
    lock_time: int = pydantic.Field(
        alias="lock_time",
    )
    output_count: int = pydantic.Field(
        alias="output_count",
    )
    output_value: float = pydantic.Field(
        alias="output_value",
    )
    size: int = pydantic.Field(
        alias="size",
    )
    version: int = pydantic.Field(
        alias="version",
    )
    virtual_size: int = pydantic.Field(
        alias="virtual_size",
    )
    weight: typing.Optional[int] = pydantic.Field(alias="weight", default=None)
