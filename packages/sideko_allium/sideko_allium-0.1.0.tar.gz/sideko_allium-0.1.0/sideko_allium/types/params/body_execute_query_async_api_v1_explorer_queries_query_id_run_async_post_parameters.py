import pydantic
import typing
import typing_extensions


class BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters(
    typing_extensions.TypedDict, total=False
):
    """
    BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters
    """


class _SerializerBodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters(
    pydantic.BaseModel
):
    """
    Serializer for BodyExecuteQueryAsyncApiV1ExplorerQueriesQueryIdRunAsyncPostParameters handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
        extra="allow",
    )
    __pydantic_extra__: typing.Dict[str, str]
