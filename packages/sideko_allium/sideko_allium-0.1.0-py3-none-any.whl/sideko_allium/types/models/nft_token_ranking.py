import pydantic
import typing_extensions


class NftTokenRanking(pydantic.BaseModel):
    """
    NftTokenRanking
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    source: typing_extensions.Literal[
        "element", "howrare", "magic_eden_instant", "moonrank"
    ] = pydantic.Field(
        alias="source",
    )
    value: int = pydantic.Field(
        alias="value",
    )
