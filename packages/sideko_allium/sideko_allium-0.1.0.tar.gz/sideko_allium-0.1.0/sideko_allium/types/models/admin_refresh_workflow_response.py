import pydantic


class AdminRefreshWorkflowResponse(pydantic.BaseModel):
    """
    AdminRefreshWorkflowResponse
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    message: str = pydantic.Field(
        alias="message",
    )
