import pydantic
import typing


class ResponseEnvelopeMultiItemsNftFullCollectionBase_(pydantic.BaseModel):
    """
    ResponseEnvelopeMultiItemsNftFullCollectionBase_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
    items: typing.Optional[typing.List[typing.Dict[str, typing.Any]]] = pydantic.Field(
        alias="items", default=None
    )
