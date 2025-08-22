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


class ResultsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list(
        self,
        *,
        run_id: str,
        f: typing.Union[
            typing.Optional[typing_extensions.Literal["csv", "json", "json_file"]],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Optional[models.QueryResult]:
        """
        Get Query Run Results

        GET /api/v1/explorer/query-runs/{run_id}/results

        Args:
            f: typing_extensions.Literal["csv", "json", "json_file"]
            run_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.query_runs.results.list(run_id="string")
        ```
        """
        _query: QueryParams = {}
        if not isinstance(f, type_utils.NotGiven):
            encode_query_param(
                _query,
                "f",
                to_encodable(
                    item=f,
                    dump_with=typing_extensions.Literal["csv", "json", "json_file"],
                ),
                style="form",
                explode=True,
            )
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/query-runs/{run_id}/results",
            auth_names=["APIKeyBearer"],
            query_params=_query,
            cast_to=typing.Optional[models.QueryResult],
            request_options=request_options or default_request_options(),
        )

    def get(
        self,
        *,
        run_id: str,
        config: typing.Union[
            typing.Optional[params.ServerSideAggregationConfig], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Optional[models.QueryResult]:
        """
        Get Query Run Results With Ssa

        POST /api/v1/explorer/query-runs/{run_id}/results

        Args:
            config: typing.Optional[ServerSideAggregationConfig]
            run_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.query_runs.results.get(run_id="string")
        ```
        """
        params._SerializerGetQueryRunResultsWithSsaBody.model_rebuild(
            _types_namespace=params._types_namespace
        )
        _json = to_encodable(
            item={"config": config},
            dump_with=params._SerializerGetQueryRunResultsWithSsaBody,
        )
        return self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/query-runs/{run_id}/results",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=typing.Optional[models.QueryResult],
            request_options=request_options or default_request_options(),
        )


class AsyncResultsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
        self,
        *,
        run_id: str,
        f: typing.Union[
            typing.Optional[typing_extensions.Literal["csv", "json", "json_file"]],
            type_utils.NotGiven,
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Optional[models.QueryResult]:
        """
        Get Query Run Results

        GET /api/v1/explorer/query-runs/{run_id}/results

        Args:
            f: typing_extensions.Literal["csv", "json", "json_file"]
            run_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.query_runs.results.list(run_id="string")
        ```
        """
        _query: QueryParams = {}
        if not isinstance(f, type_utils.NotGiven):
            encode_query_param(
                _query,
                "f",
                to_encodable(
                    item=f,
                    dump_with=typing_extensions.Literal["csv", "json", "json_file"],
                ),
                style="form",
                explode=True,
            )
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/query-runs/{run_id}/results",
            auth_names=["APIKeyBearer"],
            query_params=_query,
            cast_to=typing.Optional[models.QueryResult],
            request_options=request_options or default_request_options(),
        )

    async def get(
        self,
        *,
        run_id: str,
        config: typing.Union[
            typing.Optional[params.ServerSideAggregationConfig], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Optional[models.QueryResult]:
        """
        Get Query Run Results With Ssa

        POST /api/v1/explorer/query-runs/{run_id}/results

        Args:
            config: typing.Optional[ServerSideAggregationConfig]
            run_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.query_runs.results.get(run_id="string")
        ```
        """
        params._SerializerGetQueryRunResultsWithSsaBody.model_rebuild(
            _types_namespace=params._types_namespace
        )
        _json = to_encodable(
            item={"config": config},
            dump_with=params._SerializerGetQueryRunResultsWithSsaBody,
        )
        return await self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/query-runs/{run_id}/results",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=typing.Optional[models.QueryResult],
            request_options=request_options or default_request_options(),
        )
