import pydantic
import typing


class TableMetadataResponseItemColumn(pydantic.BaseModel):
    """
    TableMetadataResponseItemColumn
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    character_maximum_length: typing.Optional[int] = pydantic.Field(
        alias="character_maximum_length", default=None
    )
    column_name: str = pydantic.Field(
        alias="column_name",
    )
    data_type: str = pydantic.Field(
        alias="data_type",
    )
    datetime_precision: typing.Optional[int] = pydantic.Field(
        alias="datetime_precision", default=None
    )
    is_nullable: bool = pydantic.Field(
        alias="is_nullable",
    )
    numeric_precision: typing.Optional[int] = pydantic.Field(
        alias="numeric_precision", default=None
    )
    numeric_precision_radix: typing.Optional[int] = pydantic.Field(
        alias="numeric_precision_radix", default=None
    )
    numeric_scale: typing.Optional[int] = pydantic.Field(
        alias="numeric_scale", default=None
    )
    udt_name: typing.Optional[str] = pydantic.Field(alias="udt_name", default=None)
