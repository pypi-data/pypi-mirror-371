import pydantic
import typing
import typing_extensions

from .nft_price import NftPrice
from .nft_token_attribute import NftTokenAttribute
from .nft_token_metadata import NftTokenMetadata
from .nft_token_rarity import NftTokenRarity
from .solana_creator import SolanaCreator


class NftToken(pydantic.BaseModel):
    """
    NftToken
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: str = pydantic.Field(
        alias="address",
    )
    attributes: typing.Optional[typing.List[NftTokenAttribute]] = pydantic.Field(
        alias="attributes", default=None
    )
    collection_count: typing.Optional[int] = pydantic.Field(
        alias="collection_count", default=None
    )
    collection_image_url: typing.Optional[str] = pydantic.Field(
        alias="collection_image_url", default=None
    )
    collection_name: typing.Optional[str] = pydantic.Field(
        alias="collection_name", default=None
    )
    collection_symbol: typing.Optional[str] = pydantic.Field(
        alias="collection_symbol", default=None
    )
    creators: typing.Optional[typing.List[SolanaCreator]] = pydantic.Field(
        alias="creators", default=None
    )
    description: typing.Optional[str] = pydantic.Field(
        alias="description", default=None
    )
    external_url: typing.Optional[str] = pydantic.Field(
        alias="external_url", default=None
    )
    floor_price: typing.Optional[NftPrice] = pydantic.Field(
        alias="floor_price", default=None
    )
    highest_bid_price: typing.Optional[NftPrice] = pydantic.Field(
        alias="highest_bid_price", default=None
    )
    image_url: typing.Optional[str] = pydantic.Field(alias="image_url", default=None)
    last_sale_price: typing.Optional[NftPrice] = pydantic.Field(
        alias="last_sale_price", default=None
    )
    media_url: typing.Optional[str] = pydantic.Field(alias="media_url", default=None)
    metadata: typing.Optional[NftTokenMetadata] = pydantic.Field(
        alias="metadata", default=None
    )
    name: typing.Optional[str] = pydantic.Field(alias="name", default=None)
    onchain_collection_address: typing.Optional[str] = pydantic.Field(
        alias="onchain_collection_address", default=None
    )
    rarity: typing.Optional[NftTokenRarity] = pydantic.Field(
        alias="rarity", default=None
    )
    token_account_address: typing.Optional[str] = pydantic.Field(
        alias="token_account_address", default=None
    )
    token_id: typing.Optional[str] = pydantic.Field(alias="token_id", default=None)
    token_standard: typing.Optional[
        typing_extensions.Literal[
            "COMPRESSED_NFT",
            "FUNGIBLE",
            "NFT",
            "PROGRAMMABLE_NFT",
            "SEMI_FUNGIBLE",
            "UNKNOWN",
        ]
    ] = pydantic.Field(alias="token_standard", default=None)
