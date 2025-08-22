import pydantic
import typing
import typing_extensions


class StatePricesRequest(typing_extensions.TypedDict):
    """
    Request model for state prices query.
    """

    base_asset_address: typing_extensions.Required[str]
    """
    The base asset address
    """

    chain: typing_extensions.Required[str]
    """
    The blockchain name (e.g., 'ethereum', 'solana')
    """

    end_timestamp: typing_extensions.NotRequired[typing.Optional[str]]

    start_timestamp: typing_extensions.NotRequired[typing.Optional[str]]

    timestamp: typing_extensions.NotRequired[typing.Optional[str]]


class _SerializerStatePricesRequest(pydantic.BaseModel):
    """
    Serializer for StatePricesRequest handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    base_asset_address: str = pydantic.Field(
        alias="base_asset_address",
    )
    chain: str = pydantic.Field(
        alias="chain",
    )
    end_timestamp: typing.Optional[str] = pydantic.Field(
        alias="end_timestamp", default=None
    )
    start_timestamp: typing.Optional[str] = pydantic.Field(
        alias="start_timestamp", default=None
    )
    timestamp: typing.Optional[str] = pydantic.Field(alias="timestamp", default=None)
