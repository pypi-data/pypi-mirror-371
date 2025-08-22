import pydantic
import typing

from .nft_token_ranking import NftTokenRanking
from .nft_token_ranking_source_metadata import NftTokenRankingSourceMetadata


class NftTokenRarity(pydantic.BaseModel):
    """
    NftTokenRarity
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    metadata: typing.Optional[NftTokenRankingSourceMetadata] = pydantic.Field(
        alias="metadata", default=None
    )
    ranking: typing.Optional[NftTokenRanking] = pydantic.Field(
        alias="ranking", default=None
    )
