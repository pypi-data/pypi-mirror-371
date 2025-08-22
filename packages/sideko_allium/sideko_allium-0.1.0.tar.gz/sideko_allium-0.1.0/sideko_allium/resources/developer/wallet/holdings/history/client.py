import typing
import typing_extensions

from sideko_allium.core import (
    AsyncBaseClient,
    QueryParams,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    encode_query_param,
    to_encodable,
    type_utils,
)
from sideko_allium.types import models, params


class HistoryClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get(
        self,
        *,
        addresses: typing.List[params.PayloadAddress],
        end_timestamp: str,
        granularity: typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"],
        start_timestamp: str,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        include_token_breakdown: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ApiServerAppServicesHoldingsCommonModelsEnvelope:
        """
        Get Holdings History

        POST /api/v1/developer/wallet/holdings/history

        Args:
            cursor: typing.Optional[str]
            include_token_breakdown: bool
            addresses: typing.List[PayloadAddress]
            end_timestamp: str
            granularity: typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"]
            start_timestamp: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.wallet.holdings.history.get(
            addresses=[
                {
                    "address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp",
                    "chain": "solana",
                }
            ],
            end_timestamp="2025-04-10T00:00:00Z",
            granularity="1h",
            start_timestamp="2025-04-01T00:00:00Z",
            include_token_breakdown=False,
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(cursor, type_utils.NotGiven):
            encode_query_param(
                _query,
                "cursor",
                to_encodable(item=cursor, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item={
                "include_token_breakdown": include_token_breakdown,
                "addresses": addresses,
                "end_timestamp": end_timestamp,
                "granularity": granularity,
                "start_timestamp": start_timestamp,
            },
            dump_with=params._SerializerPayloadHistoricalHoldings,
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/holdings/history",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.ApiServerAppServicesHoldingsCommonModelsEnvelope,
            request_options=request_options or default_request_options(),
        )


class AsyncHistoryClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get(
        self,
        *,
        addresses: typing.List[params.PayloadAddress],
        end_timestamp: str,
        granularity: typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"],
        start_timestamp: str,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        include_token_breakdown: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ApiServerAppServicesHoldingsCommonModelsEnvelope:
        """
        Get Holdings History

        POST /api/v1/developer/wallet/holdings/history

        Args:
            cursor: typing.Optional[str]
            include_token_breakdown: bool
            addresses: typing.List[PayloadAddress]
            end_timestamp: str
            granularity: typing_extensions.Literal["15s", "1d", "1h", "1m", "5m"]
            start_timestamp: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.wallet.holdings.history.get(
            addresses=[
                {
                    "address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp",
                    "chain": "solana",
                }
            ],
            end_timestamp="2025-04-10T00:00:00Z",
            granularity="1h",
            start_timestamp="2025-04-01T00:00:00Z",
            include_token_breakdown=False,
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(cursor, type_utils.NotGiven):
            encode_query_param(
                _query,
                "cursor",
                to_encodable(item=cursor, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item={
                "include_token_breakdown": include_token_breakdown,
                "addresses": addresses,
                "end_timestamp": end_timestamp,
                "granularity": granularity,
                "start_timestamp": start_timestamp,
            },
            dump_with=params._SerializerPayloadHistoricalHoldings,
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/holdings/history",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.ApiServerAppServicesHoldingsCommonModelsEnvelope,
            request_options=request_options or default_request_options(),
        )
