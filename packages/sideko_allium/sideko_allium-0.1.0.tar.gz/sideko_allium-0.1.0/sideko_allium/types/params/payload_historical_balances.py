import pydantic
import typing
import typing_extensions

from .payload_address import PayloadAddress, _SerializerPayloadAddress


class PayloadHistoricalBalances(typing_extensions.TypedDict):
    """
    PayloadHistoricalBalances
    """

    addresses: typing_extensions.Required[typing.List[PayloadAddress]]

    end_timestamp: typing_extensions.Required[str]

    start_timestamp: typing_extensions.Required[str]


class _SerializerPayloadHistoricalBalances(pydantic.BaseModel):
    """
    Serializer for PayloadHistoricalBalances handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    addresses: typing.List[_SerializerPayloadAddress] = pydantic.Field(
        alias="addresses",
    )
    end_timestamp: str = pydantic.Field(
        alias="end_timestamp",
    )
    start_timestamp: str = pydantic.Field(
        alias="start_timestamp",
    )
