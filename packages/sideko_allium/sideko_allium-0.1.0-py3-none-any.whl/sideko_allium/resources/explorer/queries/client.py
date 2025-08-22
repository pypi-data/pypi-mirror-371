import typing

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
    type_utils,
)
from sideko_allium.types import params


class QueriesClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def run(
        self,
        *,
        data: typing.Dict[str, typing.Any],
        query_id: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Execute Query

        POST /api/v1/explorer/queries/{query_id}/run

        Args:
            data: typing.Dict[str, typing.Any]
            query_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.queries.run(data={}, query_id="string")
        ```
        """
        _json = to_encodable(item=data, dump_with=typing.Dict[str, typing.Any])
        return self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/queries/{query_id}/run",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )

    def run_async(
        self,
        *,
        parameters: typing.Optional[
            params.BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters
        ],
        query_id: str,
        run_config: typing.Union[
            typing.Optional[params.QueryRunRequestConfig], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Execute Query Async

        POST /api/v1/explorer/queries/{query_id}/run-async

        Args:
            run_config: QueryRunRequestConfig
            parameters: typing.Optional[BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters]
            query_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.queries.run_async(parameters={}, query_id="string")
        ```
        """
        _json = to_encodable(
            item={"run_config": run_config, "parameters": parameters},
            dump_with=params._SerializerBodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPost,
        )
        return self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/queries/{query_id}/run-async",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )


class AsyncQueriesClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def run(
        self,
        *,
        data: typing.Dict[str, typing.Any],
        query_id: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Execute Query

        POST /api/v1/explorer/queries/{query_id}/run

        Args:
            data: typing.Dict[str, typing.Any]
            query_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.queries.run(data={}, query_id="string")
        ```
        """
        _json = to_encodable(item=data, dump_with=typing.Dict[str, typing.Any])
        return await self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/queries/{query_id}/run",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )

    async def run_async(
        self,
        *,
        parameters: typing.Optional[
            params.BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters
        ],
        query_id: str,
        run_config: typing.Union[
            typing.Optional[params.QueryRunRequestConfig], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Execute Query Async

        POST /api/v1/explorer/queries/{query_id}/run-async

        Args:
            run_config: QueryRunRequestConfig
            parameters: typing.Optional[BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters]
            query_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.queries.run_async(parameters={}, query_id="string")
        ```
        """
        _json = to_encodable(
            item={"run_config": run_config, "parameters": parameters},
            dump_with=params._SerializerBodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPost,
        )
        return await self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/queries/{query_id}/run-async",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )
