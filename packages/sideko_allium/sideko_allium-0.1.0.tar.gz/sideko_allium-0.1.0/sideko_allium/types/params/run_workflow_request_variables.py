import pydantic
import typing
import typing_extensions


class RunWorkflowRequestVariables(typing_extensions.TypedDict, total=False):
    """
    RunWorkflowRequestVariables
    """


class _SerializerRunWorkflowRequestVariables(pydantic.BaseModel):
    """
    Serializer for RunWorkflowRequestVariables handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
        extra="allow",
    )
    __pydantic_extra__: typing.Dict[
        str,
        typing.Union[
            str,
            int,
            float,
            bool,
            typing.List[str],
            typing.List[int],
            typing.List[float],
            typing.List[bool],
        ],
    ]
