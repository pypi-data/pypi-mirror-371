import typing

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
)
from sideko_allium.types import models


class TablesClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.List[models.TableMetadataResponseItem]:
        """
        Get Table Metadata

        GET /api/v1/explorer/metadata/tables

        Args:
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.metadata.tables.list()
        ```
        """
        return self._base_client.request(
            method="GET",
            path="/api/v1/explorer/metadata/tables",
            auth_names=["APIKeyBearer"],
            cast_to=typing.List[models.TableMetadataResponseItem],
            request_options=request_options or default_request_options(),
        )

    def get(
        self, *, table_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> models.TableMetadataResponseItem:
        """
        Get Table Metadata By Id

        GET /api/v1/explorer/metadata/tables/{table_id}

        Args:
            table_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.metadata.tables.get(table_id="string")
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/metadata/tables/{table_id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.TableMetadataResponseItem,
            request_options=request_options or default_request_options(),
        )


class AsyncTablesClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.List[models.TableMetadataResponseItem]:
        """
        Get Table Metadata

        GET /api/v1/explorer/metadata/tables

        Args:
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.metadata.tables.list()
        ```
        """
        return await self._base_client.request(
            method="GET",
            path="/api/v1/explorer/metadata/tables",
            auth_names=["APIKeyBearer"],
            cast_to=typing.List[models.TableMetadataResponseItem],
            request_options=request_options or default_request_options(),
        )

    async def get(
        self, *, table_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> models.TableMetadataResponseItem:
        """
        Get Table Metadata By Id

        GET /api/v1/explorer/metadata/tables/{table_id}

        Args:
            table_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.metadata.tables.get(table_id="string")
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/explorer/metadata/tables/{table_id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.TableMetadataResponseItem,
            request_options=request_options or default_request_options(),
        )
