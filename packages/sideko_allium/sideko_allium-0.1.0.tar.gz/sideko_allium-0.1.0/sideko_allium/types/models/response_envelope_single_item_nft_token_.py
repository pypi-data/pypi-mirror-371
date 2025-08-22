import pydantic
import typing

from .nft_token import NftToken


class ResponseEnvelopeSingleItemNftToken_(pydantic.BaseModel):
    """
    ResponseEnvelopeSingleItemNftToken_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    data: typing.Optional[NftToken] = pydantic.Field(alias="data", default=None)
    error: typing.Optional[str] = pydantic.Field(alias="error", default=None)
