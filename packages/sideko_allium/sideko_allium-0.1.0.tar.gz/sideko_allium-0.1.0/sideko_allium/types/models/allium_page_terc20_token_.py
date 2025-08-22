import pydantic
import typing

from .terc20_token import Terc20Token


class AlliumPageTerc20Token_(pydantic.BaseModel):
    """
    AlliumPageTerc20Token_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[Terc20Token] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
