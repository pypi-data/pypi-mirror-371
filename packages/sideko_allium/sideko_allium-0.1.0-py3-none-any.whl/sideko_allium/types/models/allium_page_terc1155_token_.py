import pydantic
import typing

from .terc1155_token import Terc1155Token


class AlliumPageTerc1155Token_(pydantic.BaseModel):
    """
    AlliumPageTerc1155Token_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[Terc1155Token] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
