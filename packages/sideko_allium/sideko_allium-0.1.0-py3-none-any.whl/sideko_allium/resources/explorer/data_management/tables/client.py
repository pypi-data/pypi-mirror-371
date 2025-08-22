import typing

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
    type_utils,
)
from sideko_allium.types import models, params


class TablesClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def insert(
        self,
        *,
        data: typing.List[typing.Dict[str, typing.Any]],
        table_name: str,
        overwrite: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.IngestJob:
        """
        Insert data into Explorer table

        Insert rows into a private Explorer table controlled by your organization. If the table does not exist, it will be created.

        POST /api/v1/explorer/data-management/tables/{table_name}/insert

        Args:
            overwrite: bool
            data: typing.List[typing.Dict[str, typing.Any]]
            table_name: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Returns the ingest job

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.data_management.tables.insert(data=[{}], table_name="string")
        ```
        """
        _json = to_encodable(
            item={"overwrite": overwrite, "data": data},
            dump_with=params._SerializerInsertTableBody,
        )
        return self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/data-management/tables/{table_name}/insert",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.IngestJob,
            request_options=request_options or default_request_options(),
        )


class AsyncTablesClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def insert(
        self,
        *,
        data: typing.List[typing.Dict[str, typing.Any]],
        table_name: str,
        overwrite: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.IngestJob:
        """
        Insert data into Explorer table

        Insert rows into a private Explorer table controlled by your organization. If the table does not exist, it will be created.

        POST /api/v1/explorer/data-management/tables/{table_name}/insert

        Args:
            overwrite: bool
            data: typing.List[typing.Dict[str, typing.Any]]
            table_name: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Returns the ingest job

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.data_management.tables.insert(
            data=[{}], table_name="string"
        )
        ```
        """
        _json = to_encodable(
            item={"overwrite": overwrite, "data": data},
            dump_with=params._SerializerInsertTableBody,
        )
        return await self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/data-management/tables/{table_name}/insert",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.IngestJob,
            request_options=request_options or default_request_options(),
        )
