import pydantic
import typing


class NftContract(pydantic.BaseModel):
    """
    NftContract
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: str = pydantic.Field(
        alias="address",
    )
    chain: str = pydantic.Field(
        alias="chain",
    )
    collection: typing.Optional[str] = pydantic.Field(
        alias="collection",
    )
    contract_standard: typing.Optional[str] = pydantic.Field(
        alias="contract_standard",
    )
    name: typing.Optional[str] = pydantic.Field(
        alias="name",
    )
    total_supply: typing.Optional[int] = pydantic.Field(
        alias="total_supply",
    )
