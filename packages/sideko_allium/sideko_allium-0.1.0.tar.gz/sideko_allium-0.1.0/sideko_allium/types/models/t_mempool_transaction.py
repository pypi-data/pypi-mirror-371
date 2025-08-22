import pydantic
import typing


class TMempoolTransaction(pydantic.BaseModel):
    """
    Bitcoin mempool transaction entity.
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
    fee: typing.Optional[float] = pydantic.Field(alias="fee", default=None)
    fetched_at: typing.Optional[str] = pydantic.Field(alias="fetched_at", default=None)
    hash: typing.Optional[str] = pydantic.Field(alias="hash", default=None)
    input_count: typing.Optional[int] = pydantic.Field(
        alias="input_count", default=None
    )
    lock_time: typing.Optional[int] = pydantic.Field(alias="lock_time", default=None)
    output_count: typing.Optional[int] = pydantic.Field(
        alias="output_count", default=None
    )
    output_value: typing.Optional[float] = pydantic.Field(
        alias="output_value", default=None
    )
    size: typing.Optional[int] = pydantic.Field(alias="size", default=None)
    tx_id: str = pydantic.Field(
        alias="tx_id",
    )
    version: typing.Optional[int] = pydantic.Field(alias="version", default=None)
    virtual_size: typing.Optional[int] = pydantic.Field(
        alias="virtual_size", default=None
    )
    weight: typing.Optional[int] = pydantic.Field(alias="weight", default=None)
