import pydantic
import typing
import typing_extensions

from .token_attributes import TokenAttributes
from .token_info import TokenInfo


class Token(pydantic.BaseModel):
    """
    Token
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: str = pydantic.Field(
        alias="address",
    )
    attributes: typing.Optional[TokenAttributes] = pydantic.Field(
        alias="attributes", default=None
    )
    chain: str = pydantic.Field(
        alias="chain",
    )
    decimals: typing.Optional[int] = pydantic.Field(alias="decimals", default=None)
    info: typing.Optional[TokenInfo] = pydantic.Field(alias="info", default=None)
    object: typing.Optional[str] = pydantic.Field(alias="object", default=None)
    price: typing.Optional[float] = pydantic.Field(alias="price", default=None)
    type_: typing.Optional[
        typing_extensions.Literal[
            "evm_erc1155", "evm_erc20", "evm_erc721", "native", "sol_spl", "sui_token"
        ]
    ] = pydantic.Field(
        alias="type",
    )
