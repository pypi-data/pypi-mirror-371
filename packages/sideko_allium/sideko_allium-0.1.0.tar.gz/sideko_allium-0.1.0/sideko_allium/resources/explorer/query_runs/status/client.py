import typing
import typing_extensions

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
)


class StatusClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get(
        self, *, run_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Optional[
        typing_extensions.Literal[
            "canceled", "created", "failed", "queued", "running", "success"
        ]
    ]:
        """
        Get Query Run Status

        GET /api/v1/explorer/query-runs/{run_id}/status

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
        client.explorer.query_runs.status.get(run_id="string")
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/query-runs/{run_id}/status",
            auth_names=["APIKeyBearer"],
            cast_to=typing.Optional[
                typing_extensions.Literal[
                    "canceled", "created", "failed", "queued", "running", "success"
                ]
            ],
            request_options=request_options or default_request_options(),
        )


class AsyncStatusClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get(
        self, *, run_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Optional[
        typing_extensions.Literal[
            "canceled", "created", "failed", "queued", "running", "success"
        ]
    ]:
        """
        Get Query Run Status

        GET /api/v1/explorer/query-runs/{run_id}/status

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
        await client.explorer.query_runs.status.get(run_id="string")
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/query-runs/{run_id}/status",
            auth_names=["APIKeyBearer"],
            cast_to=typing.Optional[
                typing_extensions.Literal[
                    "canceled", "created", "failed", "queued", "running", "success"
                ]
            ],
            request_options=request_options or default_request_options(),
        )
