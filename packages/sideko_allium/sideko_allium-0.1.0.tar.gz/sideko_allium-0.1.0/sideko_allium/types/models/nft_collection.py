import pydantic
import typing


class NftCollection(pydantic.BaseModel):
    """
    NftCollection
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    banner_url: typing.Optional[str] = pydantic.Field(alias="banner_url", default=None)
    collection_id: typing.Optional[str] = pydantic.Field(
        alias="collection_id", default=None
    )
    description: typing.Optional[str] = pydantic.Field(
        alias="description", default=None
    )
    discord_url: typing.Optional[str] = pydantic.Field(
        alias="discord_url", default=None
    )
    external_url: typing.Optional[str] = pydantic.Field(
        alias="external_url", default=None
    )
    image_url: typing.Optional[str] = pydantic.Field(alias="image_url", default=None)
    is_spam: typing.Optional[bool] = pydantic.Field(alias="is_spam", default=None)
    name: typing.Optional[str] = pydantic.Field(alias="name", default=None)
    supply: typing.Optional[str] = pydantic.Field(alias="supply", default=None)
    symbol: typing.Optional[str] = pydantic.Field(alias="symbol", default=None)
    token_standard: typing.Optional[str] = pydantic.Field(
        alias="token_standard", default=None
    )
    twitter_url: typing.Optional[str] = pydantic.Field(
        alias="twitter_url", default=None
    )
