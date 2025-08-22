import pydantic
import typing
import typing_extensions

from .payload_token_address import PayloadTokenAddress, _SerializerPayloadTokenAddress


class PayloadTokenAddressAtTimestamp(typing_extensions.TypedDict):
    """
    PayloadTokenAddressAtTimestamp
    """

    addresses: typing_extensions.Required[typing.List[PayloadTokenAddress]]

    staleness_tolerance: typing_extensions.NotRequired[typing.Optional[str]]

    time_granularity: typing_extensions.Required[
        typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"]
    ]

    timestamp: typing_extensions.Required[str]


class _SerializerPayloadTokenAddressAtTimestamp(pydantic.BaseModel):
    """
    Serializer for PayloadTokenAddressAtTimestamp handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    addresses: typing.List[_SerializerPayloadTokenAddress] = pydantic.Field(
        alias="addresses",
    )
    staleness_tolerance: typing.Optional[str] = pydantic.Field(
        alias="staleness_tolerance", default=None
    )
    time_granularity: typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"] = (
        pydantic.Field(
            alias="time_granularity",
        )
    )
    timestamp: str = pydantic.Field(
        alias="timestamp",
    )
