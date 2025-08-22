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


class WorkflowsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def delete(
        self, *, id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> models.DeleteDataTransformationWorkflowResponse:
        """
        Delete a workflow

        Delete a workflow by ID

        DELETE /api/v1/streams/data-management/workflows/{id}

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
        client.streams.data_management.workflows.delete(id="string")
        ```
        """
        return self._base_client.request(
            method="DELETE",
            path=f"/api/v1/streams/data-management/workflows/{id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.DeleteDataTransformationWorkflowResponse,
            request_options=request_options or default_request_options(),
        )

    def list(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.List[models.DataTransformationWorkflowResponse]:
        """
        Workflows

        Get all workflows

        GET /api/v1/streams/data-management/workflows

        Args:
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.workflows.list()
        ```
        """
        return self._base_client.request(
            method="GET",
            path="/api/v1/streams/data-management/workflows",
            auth_names=["APIKeyBearer"],
            cast_to=typing.List[models.DataTransformationWorkflowResponse],
            request_options=request_options or default_request_options(),
        )

    def get(
        self, *, id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> models.DataTransformationWorkflowResponse:
        """
        Workflow by ID

        Get a workflow by ID

        GET /api/v1/streams/data-management/workflows/{id}

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
        client.streams.data_management.workflows.get(id="string")
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/streams/data-management/workflows/{id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.DataTransformationWorkflowResponse,
            request_options=request_options or default_request_options(),
        )

    def create(
        self,
        *,
        data_destination_config: typing.Union[
            params.KafkaDataDestinationMetadata,
            params.PubSubDataDestinationMetadata,
            params.StdOutDataDestinationMetadata,
        ],
        data_source_config: params.PubSubDataSourceMetadata,
        filter_id: str,
        description: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.DataTransformationWorkflowResponse:
        """
        Workflow

        Create a new workflow by specifying the description, filter, data source, and data destination

        POST /api/v1/streams/data-management/workflows

        Args:
            description: typing.Optional[str]
            data_destination_config: typing.Union[KafkaDataDestinationMetadata, PubSubDataDestinationMetadata, StdOutDataDestinationMetadata]
            data_source_config: PubSubDataSourceMetadata
            filter_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.workflows.create(
            data_destination_config={},
            data_source_config={"topic": "string"},
            filter_id="3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a",
        )
        ```
        """
        _json = to_encodable(
            item={
                "description": description,
                "data_destination_config": data_destination_config,
                "data_source_config": data_source_config,
                "filter_id": filter_id,
            },
            dump_with=params._SerializerDataTransformationWorkflowRequest,
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/streams/data-management/workflows",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.DataTransformationWorkflowResponse,
            request_options=request_options or default_request_options(),
        )

    def update(
        self,
        *,
        filter_id: str,
        id: str,
        description: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.DataTransformationWorkflowResponse:
        """
        Update a workflow

        Update a workflow by ID

        PUT /api/v1/streams/data-management/workflows/{id}

        Args:
            description: typing.Optional[str]
            filter_id: str
            id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.streams.data_management.workflows.update(
            filter_id="3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a", id="string"
        )
        ```
        """
        _json = to_encodable(
            item={"description": description, "filter_id": filter_id},
            dump_with=params._SerializerUpdateDataTransformationWorkflowRequest,
        )
        return self._base_client.request(
            method="PUT",
            path=f"/api/v1/streams/data-management/workflows/{id}",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.DataTransformationWorkflowResponse,
            request_options=request_options or default_request_options(),
        )


class AsyncWorkflowsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def delete(
        self, *, id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> models.DeleteDataTransformationWorkflowResponse:
        """
        Delete a workflow

        Delete a workflow by ID

        DELETE /api/v1/streams/data-management/workflows/{id}

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
        await client.streams.data_management.workflows.delete(id="string")
        ```
        """
        return await self._base_client.request(
            method="DELETE",
            path=f"/api/v1/streams/data-management/workflows/{id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.DeleteDataTransformationWorkflowResponse,
            request_options=request_options or default_request_options(),
        )

    async def list(
        self, *, request_options: typing.Optional[RequestOptions] = None
    ) -> typing.List[models.DataTransformationWorkflowResponse]:
        """
        Workflows

        Get all workflows

        GET /api/v1/streams/data-management/workflows

        Args:
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.workflows.list()
        ```
        """
        return await self._base_client.request(
            method="GET",
            path="/api/v1/streams/data-management/workflows",
            auth_names=["APIKeyBearer"],
            cast_to=typing.List[models.DataTransformationWorkflowResponse],
            request_options=request_options or default_request_options(),
        )

    async def get(
        self, *, id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> models.DataTransformationWorkflowResponse:
        """
        Workflow by ID

        Get a workflow by ID

        GET /api/v1/streams/data-management/workflows/{id}

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
        await client.streams.data_management.workflows.get(id="string")
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/streams/data-management/workflows/{id}",
            auth_names=["APIKeyBearer"],
            cast_to=models.DataTransformationWorkflowResponse,
            request_options=request_options or default_request_options(),
        )

    async def create(
        self,
        *,
        data_destination_config: typing.Union[
            params.KafkaDataDestinationMetadata,
            params.PubSubDataDestinationMetadata,
            params.StdOutDataDestinationMetadata,
        ],
        data_source_config: params.PubSubDataSourceMetadata,
        filter_id: str,
        description: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.DataTransformationWorkflowResponse:
        """
        Workflow

        Create a new workflow by specifying the description, filter, data source, and data destination

        POST /api/v1/streams/data-management/workflows

        Args:
            description: typing.Optional[str]
            data_destination_config: typing.Union[KafkaDataDestinationMetadata, PubSubDataDestinationMetadata, StdOutDataDestinationMetadata]
            data_source_config: PubSubDataSourceMetadata
            filter_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.workflows.create(
            data_destination_config={},
            data_source_config={"topic": "string"},
            filter_id="3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a",
        )
        ```
        """
        _json = to_encodable(
            item={
                "description": description,
                "data_destination_config": data_destination_config,
                "data_source_config": data_source_config,
                "filter_id": filter_id,
            },
            dump_with=params._SerializerDataTransformationWorkflowRequest,
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/streams/data-management/workflows",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.DataTransformationWorkflowResponse,
            request_options=request_options or default_request_options(),
        )

    async def update(
        self,
        *,
        filter_id: str,
        id: str,
        description: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.DataTransformationWorkflowResponse:
        """
        Update a workflow

        Update a workflow by ID

        PUT /api/v1/streams/data-management/workflows/{id}

        Args:
            description: typing.Optional[str]
            filter_id: str
            id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.streams.data_management.workflows.update(
            filter_id="3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a", id="string"
        )
        ```
        """
        _json = to_encodable(
            item={"description": description, "filter_id": filter_id},
            dump_with=params._SerializerUpdateDataTransformationWorkflowRequest,
        )
        return await self._base_client.request(
            method="PUT",
            path=f"/api/v1/streams/data-management/workflows/{id}",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.DataTransformationWorkflowResponse,
            request_options=request_options or default_request_options(),
        )
