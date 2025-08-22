import pydantic
import typing

from .nft_listing import NftListing


class ResponseEnvelopeMultiItemsNftListing_(pydantic.BaseModel):
    """
    ResponseEnvelopeMultiItemsNftListing_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
    items: typing.Optional[typing.List[NftListing]] = pydantic.Field(
        alias="items", default=None
    )
