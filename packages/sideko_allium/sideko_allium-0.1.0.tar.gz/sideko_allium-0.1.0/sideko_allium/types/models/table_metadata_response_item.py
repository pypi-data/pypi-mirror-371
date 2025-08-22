import pydantic
import typing

from .table_metadata_response_item_column import TableMetadataResponseItemColumn


class TableMetadataResponseItem(pydantic.BaseModel):
    """
    TableMetadataResponseItem
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    catalog_description: typing.Optional[str] = pydantic.Field(
        alias="catalog_description", default=None
    )
    catalog_name: str = pydantic.Field(
        alias="catalog_name",
    )
    columns: typing.Optional[typing.List[TableMetadataResponseItemColumn]] = (
        pydantic.Field(alias="columns", default=None)
    )
    full_namespace: typing.Optional[str] = pydantic.Field(
        alias="full_namespace", default=None
    )
    schema_description: typing.Optional[str] = pydantic.Field(
        alias="schema_description", default=None
    )
    schema_name: str = pydantic.Field(
        alias="schema_name",
    )
    table_description: typing.Optional[str] = pydantic.Field(
        alias="table_description", default=None
    )
    table_id: str = pydantic.Field(
        alias="table_id",
    )
    table_name: str = pydantic.Field(
        alias="table_name",
    )
