import pydantic
import typing
import typing_extensions

from .run_workflow_request_variables import (
    RunWorkflowRequestVariables,
    _SerializerRunWorkflowRequestVariables,
)


class RunWorkflowRequest(typing_extensions.TypedDict):
    """
    RunWorkflowRequest
    """

    variables: typing_extensions.NotRequired[
        typing.Optional[RunWorkflowRequestVariables]
    ]


class _SerializerRunWorkflowRequest(pydantic.BaseModel):
    """
    Serializer for RunWorkflowRequest handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    variables: typing.Optional[_SerializerRunWorkflowRequestVariables] = pydantic.Field(
        alias="variables", default=None
    )
