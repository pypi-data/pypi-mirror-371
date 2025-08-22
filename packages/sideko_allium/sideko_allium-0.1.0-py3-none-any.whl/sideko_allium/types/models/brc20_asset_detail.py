import pydantic
import typing
import typing_extensions


class Brc20AssetDetail(pydantic.BaseModel):
    """
    Brc20AssetDetail
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    decimals: typing.Optional[int] = pydantic.Field(alias="decimals", default=None)
    deployment_id: typing.Optional[str] = pydantic.Field(
        alias="deployment_id",
    )
    inscription_id: typing.Optional[str] = pydantic.Field(
        alias="inscription_id",
    )
    name: typing.Optional[str] = pydantic.Field(alias="name", default=None)
    symbol: typing.Optional[str] = pydantic.Field(alias="symbol", default=None)
    token_id: typing.Optional[str] = pydantic.Field(alias="token_id", default=None)
    type_: typing.Optional[
        typing_extensions.Literal["btc_brc20", "btc_inscription", "btc_rune", "native"]
    ] = pydantic.Field(
        alias="type",
    )
