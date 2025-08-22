import pydantic
import typing
import typing_extensions


class OrdinalInscriptionAssetDetail(pydantic.BaseModel):
    """
    OrdinalInscriptionAssetDetail
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    decimals: typing.Optional[int] = pydantic.Field(alias="decimals", default=None)
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
    utxo_id: typing.Optional[str] = pydantic.Field(
        alias="utxo_id",
    )
