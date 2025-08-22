import pydantic
import typing
import typing_extensions


class DataFilterAtom(typing_extensions.TypedDict):
    """
    DataFilterAtom
    """

    data_type: typing_extensions.Required[str]

    disabled: typing_extensions.NotRequired[typing.Optional[bool]]

    field: typing_extensions.Required[str]

    include_in_normalize: typing_extensions.NotRequired[typing.Optional[bool]]

    include_in_server_side_aggregation: typing_extensions.NotRequired[
        typing.Optional[bool]
    ]

    negated: typing_extensions.NotRequired[typing.Optional[bool]]

    op: typing_extensions.Required[
        typing_extensions.Literal["equal", "gt", "gte", "lt", "lte", "notIn", "oneOf"]
    ]

    value: typing_extensions.Required[typing.Any]


class _SerializerDataFilterAtom(pydantic.BaseModel):
    """
    Serializer for DataFilterAtom handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    data_type: str = pydantic.Field(
        alias="data_type",
    )
    disabled: typing.Optional[bool] = pydantic.Field(alias="disabled", default=None)
    field: str = pydantic.Field(
        alias="field",
    )
    include_in_normalize: typing.Optional[bool] = pydantic.Field(
        alias="include_in_normalize", default=None
    )
    include_in_server_side_aggregation: typing.Optional[bool] = pydantic.Field(
        alias="include_in_server_side_aggregation", default=None
    )
    negated: typing.Optional[bool] = pydantic.Field(alias="negated", default=None)
    op: typing_extensions.Literal[
        "equal", "gt", "gte", "lt", "lte", "notIn", "oneOf"
    ] = pydantic.Field(
        alias="op",
    )
    value: typing.Any = pydantic.Field(
        alias="value",
    )
