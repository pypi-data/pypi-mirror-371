import pydantic
import typing_extensions


class PayloadAddressHoldingsByToken(typing_extensions.TypedDict):
    """
    PayloadAddressHoldingsByToken
    """

    address: typing_extensions.Required[str]

    chain: typing_extensions.Required[str]

    token_address: typing_extensions.Required[str]


class _SerializerPayloadAddressHoldingsByToken(pydantic.BaseModel):
    """
    Serializer for PayloadAddressHoldingsByToken handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    address: str = pydantic.Field(
        alias="address",
    )
    chain: str = pydantic.Field(
        alias="chain",
    )
    token_address: str = pydantic.Field(
        alias="token_address",
    )
