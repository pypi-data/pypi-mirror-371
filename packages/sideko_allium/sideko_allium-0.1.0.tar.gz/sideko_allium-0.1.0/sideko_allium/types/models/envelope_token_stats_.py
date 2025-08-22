import pydantic
import typing

from .token_stats import TokenStats


class EnvelopeTokenStats_(pydantic.BaseModel):
    """
    EnvelopeTokenStats_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    items: typing.List[TokenStats] = pydantic.Field(
        alias="items",
    )
