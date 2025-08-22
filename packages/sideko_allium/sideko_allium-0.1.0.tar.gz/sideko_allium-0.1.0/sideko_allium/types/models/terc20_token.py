import pydantic
import typing


class Terc20Token(pydantic.BaseModel):
    """
    EVM ERC20 Token entity.
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Any]

    address: str = pydantic.Field(
        alias="address",
    )
    block_hash: typing.Optional[str] = pydantic.Field(alias="block_hash", default=None)
    block_number: typing.Optional[int] = pydantic.Field(
        alias="block_number", default=None
    )
    block_timestamp: str = pydantic.Field(
        alias="block_timestamp",
    )
    decimals: int = pydantic.Field(
        alias="decimals",
    )
    name: str = pydantic.Field(
        alias="name",
    )
    symbol: str = pydantic.Field(
        alias="symbol",
    )
