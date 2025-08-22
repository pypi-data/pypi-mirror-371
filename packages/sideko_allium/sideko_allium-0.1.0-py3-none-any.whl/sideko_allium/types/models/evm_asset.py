import pydantic
import typing
import typing_extensions


class EvmAsset(pydantic.BaseModel):
    """
    EvmAsset
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: typing.Optional[str] = pydantic.Field(alias="address", default=None)
    decimals: typing.Optional[int] = pydantic.Field(alias="decimals", default=None)
    name: typing.Optional[str] = pydantic.Field(alias="name", default=None)
    symbol: typing.Optional[str] = pydantic.Field(alias="symbol", default=None)
    token_id: typing.Optional[str] = pydantic.Field(alias="token_id", default=None)
    type_: typing.Optional[
        typing_extensions.Literal["evm_erc1155", "evm_erc20", "evm_erc721", "native"]
    ] = pydantic.Field(
        alias="type",
    )
