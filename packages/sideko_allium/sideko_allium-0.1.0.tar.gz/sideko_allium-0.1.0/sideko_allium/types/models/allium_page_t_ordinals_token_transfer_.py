import pydantic
import typing

from .t_ordinals_token_transfer import TOrdinalsTokenTransfer


class AlliumPageTOrdinalsTokenTransfer_(pydantic.BaseModel):
    """
    AlliumPageTOrdinalsTokenTransfer_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[TOrdinalsTokenTransfer] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
