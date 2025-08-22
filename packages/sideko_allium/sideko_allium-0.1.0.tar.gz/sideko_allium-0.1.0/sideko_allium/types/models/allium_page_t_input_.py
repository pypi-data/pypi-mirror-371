import pydantic
import typing

from .t_input import TInput


class AlliumPageTInput_(pydantic.BaseModel):
    """
    AlliumPageTInput_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[TInput] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
