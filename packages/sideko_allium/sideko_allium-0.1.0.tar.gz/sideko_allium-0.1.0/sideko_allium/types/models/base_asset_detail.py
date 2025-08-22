import pydantic
import typing
import typing_extensions


class BaseAssetDetail(pydantic.BaseModel):
    """
    BaseAssetDetail
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    decimals: typing.Optional[int] = pydantic.Field(alias="decimals", default=None)
    name: typing.Optional[str] = pydantic.Field(alias="name", default=None)
    symbol: typing.Optional[str] = pydantic.Field(alias="symbol", default=None)
    token_id: typing.Optional[str] = pydantic.Field(alias="token_id", default=None)
    type_: typing.Optional[
        typing_extensions.Literal[
            "btc_brc20",
            "btc_inscription",
            "btc_rune",
            "evm_erc1155",
            "evm_erc20",
            "evm_erc721",
            "native",
            "sol_nft",
            "sol_spl",
            "sui_token",
        ]
    ] = pydantic.Field(
        alias="type",
    )
