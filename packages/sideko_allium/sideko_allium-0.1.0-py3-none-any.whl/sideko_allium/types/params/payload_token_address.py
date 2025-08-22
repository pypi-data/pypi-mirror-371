import pydantic
import typing_extensions


class PayloadTokenAddress(typing_extensions.TypedDict):
    """
    PayloadTokenAddress
    """

    chain: typing_extensions.Required[str]

    token_address: typing_extensions.Required[str]


class _SerializerPayloadTokenAddress(pydantic.BaseModel):
    """
    Serializer for PayloadTokenAddress handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    chain: str = pydantic.Field(
        alias="chain",
    )
    token_address: str = pydantic.Field(
        alias="token_address",
    )
