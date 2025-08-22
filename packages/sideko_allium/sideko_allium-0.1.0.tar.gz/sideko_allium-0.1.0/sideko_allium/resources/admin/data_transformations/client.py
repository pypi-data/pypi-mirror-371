import typing

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
)
from sideko_allium.types import models, params


class DataTransformationsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def refresh(
        self,
        *,
        org_id: str,
        workflow_id: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.AdminRefreshWorkflowResponse:
        """
        Admin refresh a workflow

        Admin endpoint to refresh a workflow by org_id and workflow_id

        POST /admin/data-transformations/refresh

        Args:
            org_id: str
            workflow_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.admin.data_transformations.refresh(org_id="string", workflow_id="string")
        ```
        """
        _json = to_encodable(
            item={"org_id": org_id, "workflow_id": workflow_id},
            dump_with=params._SerializerAdminRefreshWorkflowRequest,
        )
        return self._base_client.request(
            method="POST",
            path="/admin/data-transformations/refresh",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.AdminRefreshWorkflowResponse,
            request_options=request_options or default_request_options(),
        )


class AsyncDataTransformationsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def refresh(
        self,
        *,
        org_id: str,
        workflow_id: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.AdminRefreshWorkflowResponse:
        """
        Admin refresh a workflow

        Admin endpoint to refresh a workflow by org_id and workflow_id

        POST /admin/data-transformations/refresh

        Args:
            org_id: str
            workflow_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.admin.data_transformations.refresh(
            org_id="string", workflow_id="string"
        )
        ```
        """
        _json = to_encodable(
            item={"org_id": org_id, "workflow_id": workflow_id},
            dump_with=params._SerializerAdminRefreshWorkflowRequest,
        )
        return await self._base_client.request(
            method="POST",
            path="/admin/data-transformations/refresh",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.AdminRefreshWorkflowResponse,
            request_options=request_options or default_request_options(),
        )
