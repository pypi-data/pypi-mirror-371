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
from sideko_allium.resources.explorer.data_management.ingest_jobs.status import (
    AsyncStatusClient,
    StatusClient,
)
from sideko_allium.types import models


class IngestJobsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.status = StatusClient(base_client=self._base_client)

    def list(
        self,
        *,
        status: typing.Union[
            typing.Optional[
                typing_extensions.Literal[
                    "completed", "failed", "queued", "running", "up_for_retry"
                ]
            ],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        table_name: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.IngestJob]:
        """
        Get Ingest Jobs

        GET /api/v1/explorer/data-management/ingest-jobs

        Args:
            status: typing.Optional[typing_extensions.Literal["completed", "failed", "queued", "running", "up_for_retry"]]
            table_name: typing.Optional[str]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.data_management.ingest_jobs.list()
        ```
        """
        _query: QueryParams = {}
        if not isinstance(status, type_utils.NotGiven):
            encode_query_param(
                _query,
                "status",
                to_encodable(
                    item=status,
                    dump_with=typing.Optional[
                        typing_extensions.Literal[
                            "completed", "failed", "queued", "running", "up_for_retry"
                        ]
                    ],
                ),
                style="form",
                explode=True,
            )
        if not isinstance(table_name, type_utils.NotGiven):
            encode_query_param(
                _query,
                "table_name",
                to_encodable(item=table_name, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        return self._base_client.request(
            method="GET",
            path="/api/v1/explorer/data-management/ingest-jobs",
            auth_names=["APIKeyBearer"],
            query_params=_query,
            cast_to=typing.List[models.IngestJob],
            request_options=request_options or default_request_options(),
        )

    def get(
        self, *, job_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> models.IngestJob:
        """
        Get Ingest Job

        GET /api/v1/explorer/data-management/ingest-jobs/{job_id}

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
        client.explorer.data_management.ingest_jobs.get(job_id="string")
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/data-management/ingest-jobs/{job_id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.IngestJob,
            request_options=request_options or default_request_options(),
        )


class AsyncIngestJobsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.status = AsyncStatusClient(base_client=self._base_client)

    async def list(
        self,
        *,
        status: typing.Union[
            typing.Optional[
                typing_extensions.Literal[
                    "completed", "failed", "queued", "running", "up_for_retry"
                ]
            ],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        table_name: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[models.IngestJob]:
        """
        Get Ingest Jobs

        GET /api/v1/explorer/data-management/ingest-jobs

        Args:
            status: typing.Optional[typing_extensions.Literal["completed", "failed", "queued", "running", "up_for_retry"]]
            table_name: typing.Optional[str]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.data_management.ingest_jobs.list()
        ```
        """
        _query: QueryParams = {}
        if not isinstance(status, type_utils.NotGiven):
            encode_query_param(
                _query,
                "status",
                to_encodable(
                    item=status,
                    dump_with=typing.Optional[
                        typing_extensions.Literal[
                            "completed", "failed", "queued", "running", "up_for_retry"
                        ]
                    ],
                ),
                style="form",
                explode=True,
            )
        if not isinstance(table_name, type_utils.NotGiven):
            encode_query_param(
                _query,
                "table_name",
                to_encodable(item=table_name, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        return await self._base_client.request(
            method="GET",
            path="/api/v1/explorer/data-management/ingest-jobs",
            auth_names=["APIKeyBearer"],
            query_params=_query,
            cast_to=typing.List[models.IngestJob],
            request_options=request_options or default_request_options(),
        )

    async def get(
        self, *, job_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> models.IngestJob:
        """
        Get Ingest Job

        GET /api/v1/explorer/data-management/ingest-jobs/{job_id}

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
        await client.explorer.data_management.ingest_jobs.get(job_id="string")
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/data-management/ingest-jobs/{job_id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.IngestJob,
            request_options=request_options or default_request_options(),
        )
