import pydantic
import typing


class TdexTrade(pydantic.BaseModel):
    """
    EVM DEX Trade entity.
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
    liquidity_pool_address: str = pydantic.Field(
        alias="liquidity_pool_address",
    )
    log_index: int = pydantic.Field(
        alias="log_index",
    )
    project: typing.Optional[str] = pydantic.Field(alias="project", default=None)
    protocol: typing.Optional[str] = pydantic.Field(alias="protocol", default=None)
    sender_address: str = pydantic.Field(
        alias="sender_address",
    )
    to_address: str = pydantic.Field(
        alias="to_address",
    )
    token_bought_amount_raw: int = pydantic.Field(
        alias="token_bought_amount_raw",
    )
    token_sold_amount_raw: int = pydantic.Field(
        alias="token_sold_amount_raw",
    )
    transaction_from_address: str = pydantic.Field(
        alias="transaction_from_address",
    )
    transaction_hash: str = pydantic.Field(
        alias="transaction_hash",
    )
    transaction_to_address: str = pydantic.Field(
        alias="transaction_to_address",
    )
