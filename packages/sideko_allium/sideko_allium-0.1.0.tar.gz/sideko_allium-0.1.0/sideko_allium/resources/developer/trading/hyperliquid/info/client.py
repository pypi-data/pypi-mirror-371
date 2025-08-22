import typing

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
)


class InfoClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get(
        self,
        *,
        data: typing.Dict[str, typing.Any],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Get Info

        POST /api/v1/developer/trading/hyperliquid/info

        Args:
            data: typing.Dict[str, typing.Any]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.trading.hyperliquid.info.get(data={})
        ```
        """
        _json = to_encodable(item=data, dump_with=typing.Dict[str, typing.Any])
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/trading/hyperliquid/info",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )


class AsyncInfoClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get(
        self,
        *,
        data: typing.Dict[str, typing.Any],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Get Info

        POST /api/v1/developer/trading/hyperliquid/info

        Args:
            data: typing.Dict[str, typing.Any]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.trading.hyperliquid.info.get(data={})
        ```
        """
        _json = to_encodable(item=data, dump_with=typing.Dict[str, typing.Any])
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/trading/hyperliquid/info",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )
