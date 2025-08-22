import pydantic
import typing
import typing_extensions


class NftListing(pydantic.BaseModel):
    """
    NftListing
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    chain: str = pydantic.Field(
        alias="chain",
    )
    contract_address: str = pydantic.Field(
        alias="contract_address",
    )
    maker: str = pydantic.Field(
        alias="maker",
    )
    price: typing.Optional[typing.Dict[str, typing.Any]] = pydantic.Field(
        alias="price", default=None
    )
    source: typing.Optional[str] = pydantic.Field(alias="source", default=None)
    status: typing.Optional[
        typing_extensions.Literal[
            "active", "cancelled", "expired", "filled", "inactive"
        ]
    ] = pydantic.Field(alias="status", default=None)
    token_id: str = pydantic.Field(
        alias="token_id",
    )
