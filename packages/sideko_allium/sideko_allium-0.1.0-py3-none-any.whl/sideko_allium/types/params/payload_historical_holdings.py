import pydantic
import typing
import typing_extensions

from .payload_address import PayloadAddress, _SerializerPayloadAddress


class PayloadHistoricalHoldings(typing_extensions.TypedDict):
    """
    PayloadHistoricalHoldings
    """

    addresses: typing_extensions.Required[typing.List[PayloadAddress]]

    end_timestamp: typing_extensions.Required[str]

    granularity: typing_extensions.Required[
        typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"]
    ]

    include_token_breakdown: typing_extensions.NotRequired[bool]

    start_timestamp: typing_extensions.Required[str]


class _SerializerPayloadHistoricalHoldings(pydantic.BaseModel):
    """
    Serializer for PayloadHistoricalHoldings handling case conversions
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
    granularity: typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"] = (
        pydantic.Field(
            alias="granularity",
        )
    )
    include_token_breakdown: typing.Optional[bool] = pydantic.Field(
        alias="include_token_breakdown", default=None
    )
    start_timestamp: str = pydantic.Field(
        alias="start_timestamp",
    )
