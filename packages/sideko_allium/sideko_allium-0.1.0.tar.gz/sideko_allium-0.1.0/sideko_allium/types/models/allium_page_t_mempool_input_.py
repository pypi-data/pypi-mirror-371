import pydantic
import typing

from .t_mempool_input import TMempoolInput


class AlliumPageTMempoolInput_(pydantic.BaseModel):
    """
    AlliumPageTMempoolInput_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[TMempoolInput] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
