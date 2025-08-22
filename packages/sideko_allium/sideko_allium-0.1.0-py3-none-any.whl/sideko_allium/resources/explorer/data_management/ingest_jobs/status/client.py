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

    def list(
        self, *, job_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing_extensions.Literal[
        "completed", "failed", "queued", "running", "up_for_retry"
    ]:
        """
        Ingest Job Status

        GET /api/v1/explorer/data-management/ingest-jobs/{job_id}/status

        Args:
            job_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.data_management.ingest_jobs.status.list(job_id="string")
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/data-management/ingest-jobs/{job_id}/status",
            auth_names=["APIKeyBearer"],
            cast_to=typing_extensions.Literal[
                "completed", "failed", "queued", "running", "up_for_retry"
            ],
            request_options=request_options or default_request_options(),
        )


class AsyncStatusClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
        self, *, job_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing_extensions.Literal[
        "completed", "failed", "queued", "running", "up_for_retry"
    ]:
        """
        Ingest Job Status

        GET /api/v1/explorer/data-management/ingest-jobs/{job_id}/status

        Args:
            job_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.data_management.ingest_jobs.status.list(job_id="string")
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/data-management/ingest-jobs/{job_id}/status",
            auth_names=["APIKeyBearer"],
            cast_to=typing_extensions.Literal[
                "completed", "failed", "queued", "running", "up_for_retry"
            ],
            request_options=request_options or default_request_options(),
        )
