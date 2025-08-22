import typing

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
)


class ErrorClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get(
        self, *, run_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Optional[str]:
        """
        Get Query Run Error

        GET /api/v1/explorer/query-runs/{run_id}/error

        Args:
            run_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.query_runs.error.get(run_id="string")
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/query-runs/{run_id}/error",
            auth_names=["APIKeyBearer"],
            cast_to=typing.Optional[str],
            request_options=request_options or default_request_options(),
        )


class AsyncErrorClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get(
        self, *, run_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Optional[str]:
        """
        Get Query Run Error

        GET /api/v1/explorer/query-runs/{run_id}/error

        Args:
            run_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.query_runs.error.get(run_id="string")
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/query-runs/{run_id}/error",
            auth_names=["APIKeyBearer"],
            cast_to=typing.Optional[str],
            request_options=request_options or default_request_options(),
        )
