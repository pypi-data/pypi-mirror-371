import pydantic
import typing_extensions


class AdminRefreshWorkflowRequest(typing_extensions.TypedDict):
    """
    AdminRefreshWorkflowRequest
    """

    org_id: typing_extensions.Required[str]

    workflow_id: typing_extensions.Required[str]


class _SerializerAdminRefreshWorkflowRequest(pydantic.BaseModel):
    """
    Serializer for AdminRefreshWorkflowRequest handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    org_id: str = pydantic.Field(
        alias="org_id",
    )
    workflow_id: str = pydantic.Field(
        alias="workflow_id",
    )
