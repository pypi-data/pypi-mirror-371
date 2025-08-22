import typing

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


class FiltersClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def delete(
        self, *, id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> models.ResponseWithId:
        """
        Delete a filter

        Delete a filter by ID

        DELETE /api/v1/streams/data-management/filters/{id}

        Args:
            id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.filters.delete(id="string")
        ```
        """
        return self._base_client.request(
            method="DELETE",
            path=f"/api/v1/streams/data-management/filters/{id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.ResponseWithId,
            request_options=request_options or default_request_options(),
        )

    def list(
        self,
        *,
        id: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Union[models.FilterResponse, typing.List[models.FilterResponse]]:
        """
        Filters

        Get all filters

        GET /api/v1/streams/data-management/filters

        Args:
            id: typing.Optional[str]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.filters.list()
        ```
        """
        _query: QueryParams = {}
        if not isinstance(id, type_utils.NotGiven):
            encode_query_param(
                _query,
                "id",
                to_encodable(item=id, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        return self._base_client.request(
            method="GET",
            path="/api/v1/streams/data-management/filters",
            auth_names=["APIKeyBearer"],
            query_params=_query,
            cast_to=typing.Union[
                models.FilterResponse, typing.List[models.FilterResponse]
            ],
            request_options=request_options or default_request_options(),
        )

    def get(
        self, *, id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Union[models.FilterResponse, typing.List[models.FilterResponse]]:
        """
        Filter by ID

        Get a filter by ID

        GET /api/v1/streams/data-management/filters/{id}

        Args:
            id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.filters.get(id="string")
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/streams/data-management/filters/{id}",
            auth_names=["APIKeyBearer"],
            cast_to=typing.Union[
                models.FilterResponse, typing.List[models.FilterResponse]
            ],
            request_options=request_options or default_request_options(),
        )

    def create(
        self,
        *,
        filter: typing.Dict[str, typing.Any],
        id: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        organization_id: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseWithId:
        """
        Filter

        Create a new filter by specifying the field, operator and type

        POST /api/v1/streams/data-management/filters

        Args:
            id: typing.Optional[str]
            organization_id: typing.Optional[str]
            filter: typing.Dict[str, typing.Any]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.filters.create(filter={})
        ```
        """
        _json = to_encodable(
            item={"id": id, "organization_id": organization_id, "filter": filter},
            dump_with=params._SerializerFilterRequest,
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/streams/data-management/filters",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.ResponseWithId,
            request_options=request_options or default_request_options(),
        )

    def update(
        self,
        *,
        filter: typing.Dict[str, typing.Any],
        id_path: str,
        id: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        organization_id: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseWithId:
        """
        Update a filter

        Update a filter by ID

        PUT /api/v1/streams/data-management/filters/{id}

        Args:
            id: typing.Optional[str]
            organization_id: typing.Optional[str]
            filter: typing.Dict[str, typing.Any]
            id_path: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.filters.update(filter={}, id_path="string")
        ```
        """
        _json = to_encodable(
            item={"id": id, "organization_id": organization_id, "filter": filter},
            dump_with=params._SerializerFilterRequest,
        )
        return self._base_client.request(
            method="PUT",
            path=f"/api/v1/streams/data-management/filters/{id_path}",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.ResponseWithId,
            request_options=request_options or default_request_options(),
        )


class AsyncFiltersClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def delete(
        self, *, id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> models.ResponseWithId:
        """
        Delete a filter

        Delete a filter by ID

        DELETE /api/v1/streams/data-management/filters/{id}

        Args:
            id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.filters.delete(id="string")
        ```
        """
        return await self._base_client.request(
            method="DELETE",
            path=f"/api/v1/streams/data-management/filters/{id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.ResponseWithId,
            request_options=request_options or default_request_options(),
        )

    async def list(
        self,
        *,
        id: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Union[models.FilterResponse, typing.List[models.FilterResponse]]:
        """
        Filters

        Get all filters

        GET /api/v1/streams/data-management/filters

        Args:
            id: typing.Optional[str]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.filters.list()
        ```
        """
        _query: QueryParams = {}
        if not isinstance(id, type_utils.NotGiven):
            encode_query_param(
                _query,
                "id",
                to_encodable(item=id, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        return await self._base_client.request(
            method="GET",
            path="/api/v1/streams/data-management/filters",
            auth_names=["APIKeyBearer"],
            query_params=_query,
            cast_to=typing.Union[
                models.FilterResponse, typing.List[models.FilterResponse]
            ],
            request_options=request_options or default_request_options(),
        )

    async def get(
        self, *, id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.Union[models.FilterResponse, typing.List[models.FilterResponse]]:
        """
        Filter by ID

        Get a filter by ID

        GET /api/v1/streams/data-management/filters/{id}

        Args:
            id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.filters.get(id="string")
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/streams/data-management/filters/{id}",
            auth_names=["APIKeyBearer"],
            cast_to=typing.Union[
                models.FilterResponse, typing.List[models.FilterResponse]
            ],
            request_options=request_options or default_request_options(),
        )

    async def create(
        self,
        *,
        filter: typing.Dict[str, typing.Any],
        id: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        organization_id: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseWithId:
        """
        Filter

        Create a new filter by specifying the field, operator and type

        POST /api/v1/streams/data-management/filters

        Args:
            id: typing.Optional[str]
            organization_id: typing.Optional[str]
            filter: typing.Dict[str, typing.Any]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.filters.create(filter={})
        ```
        """
        _json = to_encodable(
            item={"id": id, "organization_id": organization_id, "filter": filter},
            dump_with=params._SerializerFilterRequest,
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/streams/data-management/filters",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.ResponseWithId,
            request_options=request_options or default_request_options(),
        )

    async def update(
        self,
        *,
        filter: typing.Dict[str, typing.Any],
        id_path: str,
        id: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        organization_id: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseWithId:
        """
        Update a filter

        Update a filter by ID

        PUT /api/v1/streams/data-management/filters/{id}

        Args:
            id: typing.Optional[str]
            organization_id: typing.Optional[str]
            filter: typing.Dict[str, typing.Any]
            id_path: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.filters.update(filter={}, id_path="string")
        ```
        """
        _json = to_encodable(
            item={"id": id, "organization_id": organization_id, "filter": filter},
            dump_with=params._SerializerFilterRequest,
        )
        return await self._base_client.request(
            method="PUT",
            path=f"/api/v1/streams/data-management/filters/{id_path}",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.ResponseWithId,
            request_options=request_options or default_request_options(),
        )
