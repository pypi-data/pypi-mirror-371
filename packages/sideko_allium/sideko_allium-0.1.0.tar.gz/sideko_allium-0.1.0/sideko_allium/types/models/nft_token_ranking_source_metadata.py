import pydantic
import typing

from .howrare_rank import HowrareRank
from .magic_eden_instant_rank import MagicEdenInstantRank
from .moonrank_rank import MoonrankRank


class NftTokenRankingSourceMetadata(pydantic.BaseModel):
    """
    NftTokenRankingSourceMetadata
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    howrare: typing.Optional[HowrareRank] = pydantic.Field(
        alias="howrare", default=None
    )
    magic_eden_instant: typing.Optional[MagicEdenInstantRank] = pydantic.Field(
        alias="magic_eden_instant", default=None
    )
    moonrank: typing.Optional[MoonrankRank] = pydantic.Field(
        alias="moonrank", default=None
    )
