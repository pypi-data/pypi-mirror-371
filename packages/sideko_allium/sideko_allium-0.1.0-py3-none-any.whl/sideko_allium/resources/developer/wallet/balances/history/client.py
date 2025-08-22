import typing

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
        start_timestamp: str,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> (
        models.ApiServerAppServicesWalletBalancesWalletHistoricalBalancesClientEnvelope
    ):
        """
        Historical Fungible Token Balances

        Get the historical balances for a list of wallets.

        POST /api/v1/developer/wallet/balances/history

        Args:
            cursor: typing.Optional[str]
            limit: Max number of items returned. Default is 1000.
            addresses: typing.List[PayloadAddress]
            end_timestamp: str
            start_timestamp: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.wallet.balances.history.get(
            addresses=[
                {
                    "address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp",
                    "chain": "solana",
                }
            ],
            end_timestamp="2025-04-01T13:00:00Z",
            start_timestamp="2025-04-01T12:00:00Z",
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
        if not isinstance(limit, type_utils.NotGiven):
            encode_query_param(
                _query,
                "limit",
                to_encodable(item=limit, dump_with=int),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item={
                "addresses": addresses,
                "end_timestamp": end_timestamp,
                "start_timestamp": start_timestamp,
            },
            dump_with=params._SerializerPayloadHistoricalBalances,
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/balances/history",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.ApiServerAppServicesWalletBalancesWalletHistoricalBalancesClientEnvelope,
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
        start_timestamp: str,
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> (
        models.ApiServerAppServicesWalletBalancesWalletHistoricalBalancesClientEnvelope
    ):
        """
        Historical Fungible Token Balances

        Get the historical balances for a list of wallets.

        POST /api/v1/developer/wallet/balances/history

        Args:
            cursor: typing.Optional[str]
            limit: Max number of items returned. Default is 1000.
            addresses: typing.List[PayloadAddress]
            end_timestamp: str
            start_timestamp: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.wallet.balances.history.get(
            addresses=[
                {
                    "address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp",
                    "chain": "solana",
                }
            ],
            end_timestamp="2025-04-01T13:00:00Z",
            start_timestamp="2025-04-01T12:00:00Z",
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
        if not isinstance(limit, type_utils.NotGiven):
            encode_query_param(
                _query,
                "limit",
                to_encodable(item=limit, dump_with=int),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item={
                "addresses": addresses,
                "end_timestamp": end_timestamp,
                "start_timestamp": start_timestamp,
            },
            dump_with=params._SerializerPayloadHistoricalBalances,
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/balances/history",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.ApiServerAppServicesWalletBalancesWalletHistoricalBalancesClientEnvelope,
            request_options=request_options or default_request_options(),
        )
