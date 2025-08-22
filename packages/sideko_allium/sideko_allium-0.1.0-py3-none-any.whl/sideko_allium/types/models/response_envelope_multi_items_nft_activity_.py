import pydantic
import typing

from .nft_activity import NftActivity


class ResponseEnvelopeMultiItemsNftActivity_(pydantic.BaseModel):
    """
    ResponseEnvelopeMultiItemsNftActivity_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
    items: typing.Optional[typing.List[NftActivity]] = pydantic.Field(
        alias="items", default=None
    )
