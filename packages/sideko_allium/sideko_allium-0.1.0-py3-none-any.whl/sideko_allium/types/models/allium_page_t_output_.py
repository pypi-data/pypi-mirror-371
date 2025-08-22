import pydantic
import typing

from .t_output import TOutput


class AlliumPageTOutput_(pydantic.BaseModel):
    """
    AlliumPageTOutput_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[TOutput] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
