import pydantic
import typing
import typing_extensions


class ServerSideAggregationApply(typing_extensions.TypedDict):
    """
    ServerSideAggregationApply
    """

    args_after: typing_extensions.NotRequired[
        typing.Optional[typing.List[typing.Union[str, int, bool]]]
    ]

    args_before: typing_extensions.NotRequired[
        typing.Optional[typing.List[typing.Union[str, int, bool]]]
    ]

    func: typing_extensions.Required[str]


class _SerializerServerSideAggregationApply(pydantic.BaseModel):
    """
    Serializer for ServerSideAggregationApply handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    args_after: typing.Optional[typing.List[typing.Union[str, int, bool]]] = (
        pydantic.Field(alias="args_after", default=None)
    )
    args_before: typing.Optional[typing.List[typing.Union[str, int, bool]]] = (
        pydantic.Field(alias="args_before", default=None)
    )
    func: str = pydantic.Field(
        alias="func",
    )
