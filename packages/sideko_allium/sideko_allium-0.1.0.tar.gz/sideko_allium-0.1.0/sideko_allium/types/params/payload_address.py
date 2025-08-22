import pydantic
import typing_extensions


class PayloadAddress(typing_extensions.TypedDict):
    """
    PayloadAddress
    """

    address: typing_extensions.Required[str]

    chain: typing_extensions.Required[str]


class _SerializerPayloadAddress(pydantic.BaseModel):
    """
    Serializer for PayloadAddress handling case conversions
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
