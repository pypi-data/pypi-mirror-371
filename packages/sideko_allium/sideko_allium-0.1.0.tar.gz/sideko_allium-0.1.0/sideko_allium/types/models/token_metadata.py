import pydantic
import typing


class TokenMetadata(pydantic.BaseModel):
    """
    TokenMetadata
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    price: typing.Optional[float] = pydantic.Field(alias="price", default=None)
    symbol: typing.Optional[str] = pydantic.Field(alias="symbol", default=None)
    token_decimals: typing.Optional[int] = pydantic.Field(
        alias="token_decimals", default=None
    )
    token_name: typing.Optional[str] = pydantic.Field(alias="token_name", default=None)
