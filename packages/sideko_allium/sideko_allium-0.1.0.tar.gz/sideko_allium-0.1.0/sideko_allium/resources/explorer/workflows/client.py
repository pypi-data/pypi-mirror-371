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


class WorkflowsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def run(
        self,
        *,
        workflow_id: str,
        variables: typing.Union[
            typing.Optional[params.RunWorkflowRequestVariables], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Run Workflow

        POST /api/v1/explorer/workflows/{workflow_id}/run

        Args:
            variables: typing.Optional[RunWorkflowRequestVariables]
            workflow_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.explorer.workflows.run(workflow_id="string")
        ```
        """
        _json = to_encodable(
            item={"variables": variables},
            dump_with=params._SerializerRunWorkflowRequest,
        )
        return self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/workflows/{workflow_id}/run",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )


class AsyncWorkflowsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def run(
        self,
        *,
        workflow_id: str,
        variables: typing.Union[
            typing.Optional[params.RunWorkflowRequestVariables], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.Any:
        """
        Run Workflow

        POST /api/v1/explorer/workflows/{workflow_id}/run

        Args:
            variables: typing.Optional[RunWorkflowRequestVariables]
            workflow_id: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.explorer.workflows.run(workflow_id="string")
        ```
        """
        _json = to_encodable(
            item={"variables": variables},
            dump_with=params._SerializerRunWorkflowRequest,
        )
        return await self._base_client.request(
            method="POST",
            path=f"/api/v1/explorer/workflows/{workflow_id}/run",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=type(typing.Any),
            request_options=request_options or default_request_options(),
        )
