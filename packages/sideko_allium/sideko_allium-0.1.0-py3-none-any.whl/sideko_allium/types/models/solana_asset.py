import pydantic
import typing
import typing_extensions


class SolanaAsset(pydantic.BaseModel):
    """
    SolanaAsset
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
        typing_extensions.Literal["native", "sol_nft", "sol_spl"]
    ] = pydantic.Field(
        alias="type",
    )
