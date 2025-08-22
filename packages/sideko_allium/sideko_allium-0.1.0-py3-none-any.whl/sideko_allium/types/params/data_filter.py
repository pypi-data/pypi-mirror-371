import pydantic
import typing
import typing_extensions

from .data_filter_atom import DataFilterAtom, _SerializerDataFilterAtom


class DataFilter(typing_extensions.TypedDict):
    """
    DataFilter
    """

    atoms: typing_extensions.Required[
        typing.List[typing.Union["DataFilter", DataFilterAtom]]
    ]

    composition: typing_extensions.Required[typing_extensions.Literal["and", "or"]]

    disabled: typing_extensions.NotRequired[typing.Optional[bool]]

    name: typing_extensions.NotRequired[typing.Optional[str]]


class _SerializerDataFilter(pydantic.BaseModel):
    """
    Serializer for DataFilter handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    atoms: typing.List[
        typing.Union["_SerializerDataFilter", _SerializerDataFilterAtom]
    ] = pydantic.Field(
        alias="atoms",
    )
    composition: typing_extensions.Literal["and", "or"] = pydantic.Field(
        alias="composition",
    )
    disabled: typing.Optional[bool] = pydantic.Field(alias="disabled", default=None)
    name: typing.Optional[str] = pydantic.Field(alias="name", default=None)
