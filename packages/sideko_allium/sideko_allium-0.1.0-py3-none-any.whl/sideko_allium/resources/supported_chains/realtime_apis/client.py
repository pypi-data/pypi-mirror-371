import typing
import typing_extensions

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
)
from sideko_allium.types import params


class RealtimeApisClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get_endpoints(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Any:
        """
        Get Supported Endpoints

        GET /api/v1/supported-chains/realtime-apis

        Args:
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.supported_chains.realtime_apis.get_endpoints()
        ```
        """
        return self._base_client.request(
            method="GET",
            path="/api/v1/supported-chains/realtime-apis",
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )

    def get_chains(
        self,
        *,
        endpoints: typing.List[
            typing_extensions.Literal[
                "custom_sql",
                "historical_fungible_token_balances",
                "latest_fungible_token_balances",
                "latest_nft_balances",
                "nft_apis",
                "pnl",
                "token_latest_price",
                "token_price_historical",
                "token_price_stats",
                "wallet_transactions",
            ]
        ],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Get Supported Chains

        POST /api/v1/supported-chains/realtime-apis

        Args:
            endpoints: typing.List[typing_extensions.Literal["custom_sql", "historical_fungible_token_balances", "latest_fungible_token_balances", "latest_nft_balances", "nft_apis", "pnl", "token_latest_price", "token_price_historical", "token_price_stats", "wallet_transactions"]]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.supported_chains.realtime_apis.get_chains(endpoints=["custom_sql"])
        ```
        """
        _json = to_encodable(
            item={"endpoints": endpoints}, dump_with=params._SerializerEndpointsRequest
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/supported-chains/realtime-apis",
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )


class AsyncRealtimeApisClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get_endpoints(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Any:
        """
        Get Supported Endpoints

        GET /api/v1/supported-chains/realtime-apis

        Args:
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.supported_chains.realtime_apis.get_endpoints()
        ```
        """
        return await self._base_client.request(
            method="GET",
            path="/api/v1/supported-chains/realtime-apis",
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )

    async def get_chains(
        self,
        *,
        endpoints: typing.List[
            typing_extensions.Literal[
                "custom_sql",
                "historical_fungible_token_balances",
                "latest_fungible_token_balances",
                "latest_nft_balances",
                "nft_apis",
                "pnl",
                "token_latest_price",
                "token_price_historical",
                "token_price_stats",
                "wallet_transactions",
            ]
        ],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Get Supported Chains

        POST /api/v1/supported-chains/realtime-apis

        Args:
            endpoints: typing.List[typing_extensions.Literal["custom_sql", "historical_fungible_token_balances", "latest_fungible_token_balances", "latest_nft_balances", "nft_apis", "pnl", "token_latest_price", "token_price_historical", "token_price_stats", "wallet_transactions"]]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.supported_chains.realtime_apis.get_chains(endpoints=["custom_sql"])
        ```
        """
        _json = to_encodable(
            item={"endpoints": endpoints}, dump_with=params._SerializerEndpointsRequest
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/supported-chains/realtime-apis",
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )
