import typing

from sideko_allium.core import (
    AsyncBaseClient,
    QueryParams,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    encode_query_param,
    to_encodable,
)
from sideko_allium.resources.explorer.query_runs.error import (
    AsyncErrorClient,
    ErrorClient,
)
from sideko_allium.resources.explorer.query_runs.results import (
    AsyncResultsClient,
    ResultsClient,
)
from sideko_allium.resources.explorer.query_runs.status import (
    AsyncStatusClient,
    StatusClient,
)
from sideko_allium.types import models


class QueryRunsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.error = ErrorClient(base_client=self._base_client)
        self.results = ResultsClient(base_client=self._base_client)
        self.status = StatusClient(base_client=self._base_client)

    def list(
        self, *, query_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Optional[models.QueryRun]:
        """
        Get Latest Query Run Handler

        GET /api/v1/explorer/query-runs

        Args:
            query_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.query_runs.list(query_id="string")
        ```
        """
        _query: QueryParams = {}
        encode_query_param(
            _query,
            "query_id",
            to_encodable(item=query_id, dump_with=str),
            style="form",
            explode=True,
        )
        return self._base_client.request(
            method="GET",
            path="/api/v1/explorer/query-runs",
            auth_names=["APIKeyBearer"],
            query_params=_query,
            cast_to=typing.Optional[models.QueryRun],
            request_options=request_options or default_request_options(),
        )

    def get(
        self, *, run_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Optional[models.QueryRun]:
        """
        Get Query Run Handler

        GET /api/v1/explorer/query-runs/{run_id}

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
        client.explorer.query_runs.get(run_id="string")
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/query-runs/{run_id}",
            auth_names=["APIKeyBearer"],
            cast_to=typing.Optional[models.QueryRun],
            request_options=request_options or default_request_options(),
        )

    def cancel(
        self, *, run_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Any:
        """
        Cancel Query Run

        POST /api/v1/explorer/query-runs/{run_id}/cancel

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
        client.explorer.query_runs.cancel(run_id="string")
        ```
        """
        return self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/query-runs/{run_id}/cancel",
            auth_names=["APIKeyBearer"],
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )


class AsyncQueryRunsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.error = AsyncErrorClient(base_client=self._base_client)
        self.results = AsyncResultsClient(base_client=self._base_client)
        self.status = AsyncStatusClient(base_client=self._base_client)

    async def list(
        self, *, query_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Optional[models.QueryRun]:
        """
        Get Latest Query Run Handler

        GET /api/v1/explorer/query-runs

        Args:
            query_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.query_runs.list(query_id="string")
        ```
        """
        _query: QueryParams = {}
        encode_query_param(
            _query,
            "query_id",
            to_encodable(item=query_id, dump_with=str),
            style="form",
            explode=True,
        )
        return await self._base_client.request(
            method="GET",
            path="/api/v1/explorer/query-runs",
            auth_names=["APIKeyBearer"],
            query_params=_query,
            cast_to=typing.Optional[models.QueryRun],
            request_options=request_options or default_request_options(),
        )

    async def get(
        self, *, run_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Optional[models.QueryRun]:
        """
        Get Query Run Handler

        GET /api/v1/explorer/query-runs/{run_id}

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
        await client.explorer.query_runs.get(run_id="string")
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/query-runs/{run_id}",
            auth_names=["APIKeyBearer"],
            cast_to=typing.Optional[models.QueryRun],
            request_options=request_options or default_request_options(),
        )

    async def cancel(
        self, *, run_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Any:
        """
        Cancel Query Run

        POST /api/v1/explorer/query-runs/{run_id}/cancel

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
        await client.explorer.query_runs.cancel(run_id="string")
        ```
        """
        return await self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/query-runs/{run_id}/cancel",
            auth_names=["APIKeyBearer"],
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )
