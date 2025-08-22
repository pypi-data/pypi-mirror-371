import typing
import typing_extensions

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
)
from sideko_allium.types import models, params


class FilterDataSourcesClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def delete(
        self,
        *,
        data_source_id: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseWithId:
        """
        Delete a filter data source

        Delete a filter data source by ID. Will fail if the data source is being used by any filters.

        DELETE /api/v1/streams/data-management/filter-data-sources/{data_source_id}

        Args:
            data_source_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.filter_data_sources.delete(
            data_source_id="string"
        )
        ```
        """
        return self._base_client.request(
            method="DELETE",
            path=f"/api/v1/streams/data-management/filter-data-sources/{data_source_id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.ResponseWithId,
            request_options=request_options or default_request_options(),
        )

    def list(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.List[models.FilterDataSourceResponse]:
        """
        Filter Data Sources

        Get all filter data sources

        GET /api/v1/streams/data-management/filter-data-sources

        Args:
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.filter_data_sources.list()
        ```
        """
        return self._base_client.request(
            method="GET",
            path="/api/v1/streams/data-management/filter-data-sources",
            auth_names=["APIKeyBearer"],
            cast_to=typing.List[models.FilterDataSourceResponse],
            request_options=request_options or default_request_options(),
        )

    def get(
        self,
        *,
        data_source_id: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.FilterDataSourceResponse:
        """
        Filter Data Source by ID

        Get a filter data source by ID

        GET /api/v1/streams/data-management/filter-data-sources/{data_source_id}

        Args:
            data_source_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.filter_data_sources.get(data_source_id="string")
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/streams/data-management/filter-data-sources/{data_source_id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.FilterDataSourceResponse,
            request_options=request_options or default_request_options(),
        )

    def create(
        self,
        *,
        description: str,
        name: str,
        type_: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseWithId:
        """
        Filter Data Source

        Create a new filter data source by specifying the name and type

        POST /api/v1/streams/data-management/filter-data-sources

        Args:
            description: str
            name: str
            type: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.filter_data_sources.create(
            description="string", name="string", type_="string"
        )
        ```
        """
        _json = to_encodable(
            item={"description": description, "name": name, "type_": type_},
            dump_with=params._SerializerFilterDataSourceRequest,
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/streams/data-management/filter-data-sources",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.ResponseWithId,
            request_options=request_options or default_request_options(),
        )

    def update_values(
        self,
        *,
        data_source_id: str,
        operation: typing_extensions.Literal["ADD", "DELETE"],
        values: typing.List[str],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.FilterDataSourceValuesResponse:
        """
        Filter Data Source Values

        Update values for a filter data source

        POST /api/v1/streams/data-management/filter-data-sources/{data_source_id}/values

        Args:
            data_source_id: str
            operation: typing_extensions.Literal["ADD", "DELETE"]
            values: typing.List[str]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.filter_data_sources.update_values(
            data_source_id="string", operation="ADD", values=["string"]
        )
        ```
        """
        _json = to_encodable(
            item={"operation": operation, "values": values},
            dump_with=params._SerializerFilterDataSourceValuesRequest,
        )
        return self._base_client.request(
            method="POST",
            path=f"/api/v1/streams/data-management/filter-data-sources/{data_source_id}/values",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.FilterDataSourceValuesResponse,
            request_options=request_options or default_request_options(),
        )


class AsyncFilterDataSourcesClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def delete(
        self,
        *,
        data_source_id: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseWithId:
        """
        Delete a filter data source

        Delete a filter data source by ID. Will fail if the data source is being used by any filters.

        DELETE /api/v1/streams/data-management/filter-data-sources/{data_source_id}

        Args:
            data_source_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.filter_data_sources.delete(
            data_source_id="string"
        )
        ```
        """
        return await self._base_client.request(
            method="DELETE",
            path=f"/api/v1/streams/data-management/filter-data-sources/{data_source_id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.ResponseWithId,
            request_options=request_options or default_request_options(),
        )

    async def list(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.List[models.FilterDataSourceResponse]:
        """
        Filter Data Sources

        Get all filter data sources

        GET /api/v1/streams/data-management/filter-data-sources

        Args:
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.filter_data_sources.list()
        ```
        """
        return await self._base_client.request(
            method="GET",
            path="/api/v1/streams/data-management/filter-data-sources",
            auth_names=["APIKeyBearer"],
            cast_to=typing.List[models.FilterDataSourceResponse],
            request_options=request_options or default_request_options(),
        )

    async def get(
        self,
        *,
        data_source_id: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.FilterDataSourceResponse:
        """
        Filter Data Source by ID

        Get a filter data source by ID

        GET /api/v1/streams/data-management/filter-data-sources/{data_source_id}

        Args:
            data_source_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.filter_data_sources.get(
            data_source_id="string"
        )
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/streams/data-management/filter-data-sources/{data_source_id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.FilterDataSourceResponse,
            request_options=request_options or default_request_options(),
        )

    async def create(
        self,
        *,
        description: str,
        name: str,
        type_: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseWithId:
        """
        Filter Data Source

        Create a new filter data source by specifying the name and type

        POST /api/v1/streams/data-management/filter-data-sources

        Args:
            description: str
            name: str
            type: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.filter_data_sources.create(
            description="string", name="string", type_="string"
        )
        ```
        """
        _json = to_encodable(
            item={"description": description, "name": name, "type_": type_},
            dump_with=params._SerializerFilterDataSourceRequest,
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/streams/data-management/filter-data-sources",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.ResponseWithId,
            request_options=request_options or default_request_options(),
        )

    async def update_values(
        self,
        *,
        data_source_id: str,
        operation: typing_extensions.Literal["ADD", "DELETE"],
        values: typing.List[str],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.FilterDataSourceValuesResponse:
        """
        Filter Data Source Values

        Update values for a filter data source

        POST /api/v1/streams/data-management/filter-data-sources/{data_source_id}/values

        Args:
            data_source_id: str
            operation: typing_extensions.Literal["ADD", "DELETE"]
            values: typing.List[str]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.filter_data_sources.update_values(
            data_source_id="string", operation="ADD", values=["string"]
        )
        ```
        """
        _json = to_encodable(
            item={"operation": operation, "values": values},
            dump_with=params._SerializerFilterDataSourceValuesRequest,
        )
        return await self._base_client.request(
            method="POST",
            path=f"/api/v1/streams/data-management/filter-data-sources/{data_source_id}/values",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.FilterDataSourceValuesResponse,
            request_options=request_options or default_request_options(),
        )
