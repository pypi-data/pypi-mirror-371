import pydantic
import typing
import typing_extensions


class InsertTableBody(typing_extensions.TypedDict):
    """
    InsertTableBody
    """

    data: typing_extensions.Required[typing.List[typing.Dict[str, typing.Any]]]

    overwrite: typing_extensions.NotRequired[bool]


class _SerializerInsertTableBody(pydantic.BaseModel):
    """
    Serializer for InsertTableBody handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    data: typing.List[typing.Dict[str, typing.Any]] = pydantic.Field(
        alias="data",
    )
    overwrite: typing.Optional[bool] = pydantic.Field(alias="overwrite", default=None)
