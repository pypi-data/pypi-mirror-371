import typing

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
    type_utils,
)
from sideko_allium.types import models, params


class HistoricalClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list(
        self,
        *,
        base_asset_address: str,
        chain: str,
        end_timestamp: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        start_timestamp: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        timestamp: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeMultiItemsLiquidityPoolStateData_:
        """
        Get State Prices

        Get state prices for a given chain and base asset address. Supports both single timestamp queries and time range queries.

        POST /api/v1/developer/state-prices/historical

        Args:
            end_timestamp: typing.Optional[str]
            start_timestamp: typing.Optional[str]
            timestamp: typing.Optional[str]
            base_asset_address: The base asset address
            chain: The blockchain name (e.g., 'ethereum', 'solana')
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.state_prices.historical.list(
            base_asset_address="string", chain="string"
        )
        ```
        """
        _json = to_encodable(
            item={
                "end_timestamp": end_timestamp,
                "start_timestamp": start_timestamp,
                "timestamp": timestamp,
                "base_asset_address": base_asset_address,
                "chain": chain,
            },
            dump_with=params._SerializerStatePricesRequest,
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/state-prices/historical",
            json=_json,
            cast_to=models.ResponseEnvelopeMultiItemsLiquidityPoolStateData_,
            request_options=request_options or default_request_options(),
        )


class AsyncHistoricalClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
        self,
        *,
        base_asset_address: str,
        chain: str,
        end_timestamp: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        start_timestamp: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        timestamp: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeMultiItemsLiquidityPoolStateData_:
        """
        Get State Prices

        Get state prices for a given chain and base asset address. Supports both single timestamp queries and time range queries.

        POST /api/v1/developer/state-prices/historical

        Args:
            end_timestamp: typing.Optional[str]
            start_timestamp: typing.Optional[str]
            timestamp: typing.Optional[str]
            base_asset_address: The base asset address
            chain: The blockchain name (e.g., 'ethereum', 'solana')
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.state_prices.historical.list(
            base_asset_address="string", chain="string"
        )
        ```
        """
        _json = to_encodable(
            item={
                "end_timestamp": end_timestamp,
                "start_timestamp": start_timestamp,
                "timestamp": timestamp,
                "base_asset_address": base_asset_address,
                "chain": chain,
            },
            dump_with=params._SerializerStatePricesRequest,
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/state-prices/historical",
            json=_json,
            cast_to=models.ResponseEnvelopeMultiItemsLiquidityPoolStateData_,
            request_options=request_options or default_request_options(),
        )
