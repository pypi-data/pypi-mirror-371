import typing

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
)


class SnapshotClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Any:
        """
        Orderbook Snapshot

        GET /api/v1/developer/trading/hyperliquid/orderbook/snapshot

        Args:
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.trading.hyperliquid.orderbook.snapshot.list()
        ```
        """
        return self._base_client.request(
            method="GET",
            path="/api/v1/developer/trading/hyperliquid/orderbook/snapshot",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )


class AsyncSnapshotClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Any:
        """
        Orderbook Snapshot

        GET /api/v1/developer/trading/hyperliquid/orderbook/snapshot

        Args:
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.trading.hyperliquid.orderbook.snapshot.list()
        ```
        """
        return await self._base_client.request(
            method="GET",
            path="/api/v1/developer/trading/hyperliquid/orderbook/snapshot",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )
