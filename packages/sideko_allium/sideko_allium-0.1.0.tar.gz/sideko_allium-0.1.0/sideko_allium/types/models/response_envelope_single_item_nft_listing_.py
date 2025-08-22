import pydantic
import typing

from .nft_listing import NftListing


class ResponseEnvelopeSingleItemNftListing_(pydantic.BaseModel):
    """
    ResponseEnvelopeSingleItemNftListing_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    data: typing.Optional[NftListing] = pydantic.Field(alias="data", default=None)
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
