import pydantic
import typing_extensions


class PayloadPriceHistoricalLegacy(typing_extensions.TypedDict):
    """
    PayloadPriceHistoricalLegacy
    """

    chain: typing_extensions.Required[str]

    end_timestamp: typing_extensions.Required[str]

    start_timestamp: typing_extensions.Required[str]

    time_granularity: typing_extensions.Required[
        typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"]
    ]

    token_address: typing_extensions.Required[str]


class _SerializerPayloadPriceHistoricalLegacy(pydantic.BaseModel):
    """
    Serializer for PayloadPriceHistoricalLegacy handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    chain: str = pydantic.Field(
        alias="chain",
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
    token_address: str = pydantic.Field(
        alias="token_address",
    )
