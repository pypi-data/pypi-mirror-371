import pydantic
import typing
import typing_extensions

from .payload_address import PayloadAddress, _SerializerPayloadAddress


class PayloadHistoricalPnlByWallet(typing_extensions.TypedDict):
    """
    PayloadHistoricalPnlByWallet
    """

    addresses: typing_extensions.Required[typing.List[PayloadAddress]]

    end_timestamp: typing_extensions.Required[str]

    granularity: typing_extensions.Required[typing_extensions.Literal["1d", "1h"]]

    start_timestamp: typing_extensions.Required[str]


class _SerializerPayloadHistoricalPnlByWallet(pydantic.BaseModel):
    """
    Serializer for PayloadHistoricalPnlByWallet handling case conversions
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
    granularity: typing_extensions.Literal["1d", "1h"] = pydantic.Field(
        alias="granularity",
    )
    start_timestamp: str = pydantic.Field(
        alias="start_timestamp",
    )
