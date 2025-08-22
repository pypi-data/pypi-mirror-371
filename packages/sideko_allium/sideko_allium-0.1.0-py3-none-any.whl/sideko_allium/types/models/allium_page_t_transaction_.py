import pydantic
import typing

from .t_transaction import TTransaction


class AlliumPageTTransaction_(pydantic.BaseModel):
    """
    AlliumPageTTransaction_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[TTransaction] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
