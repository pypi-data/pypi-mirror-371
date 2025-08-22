import pydantic
import typing
import typing_extensions

from .payload_token_address import PayloadTokenAddress, _SerializerPayloadTokenAddress


class PayloadPriceHistorical(typing_extensions.TypedDict):
    """
    PayloadPriceHistorical
    """

    addresses: typing_extensions.Required[typing.List[PayloadTokenAddress]]

    end_timestamp: typing_extensions.Required[str]

    start_timestamp: typing_extensions.Required[str]

    time_granularity: typing_extensions.Required[
        typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"]
    ]


class _SerializerPayloadPriceHistorical(pydantic.BaseModel):
    """
    Serializer for PayloadPriceHistorical handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    addresses: typing.List[_SerializerPayloadTokenAddress] = pydantic.Field(
        alias="addresses",
    )
    end_timestamp: str = pydantic.Field(
        alias="end_timestamp",
    )
    start_timestamp: str = pydantic.Field(
        alias="start_timestamp",
    )
    time_granularity: typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"] = (
        pydantic.Field(
            alias="time_granularity",
        )
    )
