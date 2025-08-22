import pydantic
import typing
import typing_extensions


class UpdateDataTransformationWorkflowRequest(typing_extensions.TypedDict):
    """
    UpdateDataTransformationWorkflowRequest
    """

    description: typing_extensions.NotRequired[typing.Optional[str]]

    filter_id: typing_extensions.Required[str]


class _SerializerUpdateDataTransformationWorkflowRequest(pydantic.BaseModel):
    """
    Serializer for UpdateDataTransformationWorkflowRequest handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    description: typing.Optional[str] = pydantic.Field(
        alias="description", default=None
    )
    filter_id: str = pydantic.Field(
        alias="filter_id",
    )
