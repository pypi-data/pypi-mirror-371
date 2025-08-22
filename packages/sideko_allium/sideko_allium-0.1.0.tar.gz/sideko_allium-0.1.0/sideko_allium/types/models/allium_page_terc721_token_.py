import pydantic
import typing

from .terc721_token import Terc721Token


class AlliumPageTerc721Token_(pydantic.BaseModel):
    """
    AlliumPageTerc721Token_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[Terc721Token] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
