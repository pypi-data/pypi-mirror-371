import pydantic
import typing
import typing_extensions

from .payload_address_holdings_by_token import (
    PayloadAddressHoldingsByToken,
    _SerializerPayloadAddressHoldingsByToken,
)


class PayloadHistoricalPnlByToken(typing_extensions.TypedDict):
    """
    PayloadHistoricalPnlByToken
    """

    addresses: typing_extensions.Required[typing.List[PayloadAddressHoldingsByToken]]

    end_timestamp: typing_extensions.Required[str]

    granularity: typing_extensions.Required[typing_extensions.Literal["1d", "1h"]]

    start_timestamp: typing_extensions.Required[str]


class _SerializerPayloadHistoricalPnlByToken(pydantic.BaseModel):
    """
    Serializer for PayloadHistoricalPnlByToken handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    addresses: typing.List[_SerializerPayloadAddressHoldingsByToken] = pydantic.Field(
        alias="addresses",
    )
    end_timestamp: str = pydantic.Field(
        alias="end_timestamp",
    )
    granularity: typing_extensions.Literal["1d", "1h"] = pydantic.Field(
        alias="granularity",
    )
    start_timestamp: str = pydantic.Field(
        alias="start_timestamp",
    )
