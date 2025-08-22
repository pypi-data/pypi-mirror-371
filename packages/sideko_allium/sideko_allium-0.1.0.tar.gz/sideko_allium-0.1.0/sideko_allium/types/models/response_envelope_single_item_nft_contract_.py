import pydantic
import typing

from .nft_contract import NftContract


class ResponseEnvelopeSingleItemNftContract_(pydantic.BaseModel):
    """
    ResponseEnvelopeSingleItemNftContract_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    data: typing.Optional[NftContract] = pydantic.Field(alias="data", default=None)
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
