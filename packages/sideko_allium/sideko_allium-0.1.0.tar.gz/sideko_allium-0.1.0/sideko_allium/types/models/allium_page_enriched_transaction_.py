import pydantic
import typing

from .enriched_transaction import EnrichedTransaction


class AlliumPageEnrichedTransaction_(pydantic.BaseModel):
    """
    AlliumPageEnrichedTransaction_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[EnrichedTransaction] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
