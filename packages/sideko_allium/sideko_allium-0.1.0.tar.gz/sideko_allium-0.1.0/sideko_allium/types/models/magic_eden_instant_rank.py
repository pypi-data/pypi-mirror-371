import pydantic
import typing


class MagicEdenInstantRank(pydantic.BaseModel):
    """
    MagicEdenInstantRank
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    rank: typing.Optional[int] = pydantic.Field(alias="rank", default=None)
