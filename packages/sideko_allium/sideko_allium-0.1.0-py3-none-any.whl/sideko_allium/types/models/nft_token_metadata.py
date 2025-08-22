import pydantic
import typing


class NftTokenMetadata(pydantic.BaseModel):
    """
    NftTokenMetadata
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    image_mime_type: typing.Optional[str] = pydantic.Field(
        alias="image_mime_type", default=None
    )
    image_original: typing.Optional[str] = pydantic.Field(
        alias="image_original", default=None
    )
    media_original: typing.Optional[str] = pydantic.Field(
        alias="media_original", default=None
    )
    token_uri: typing.Optional[str] = pydantic.Field(alias="token_uri", default=None)
