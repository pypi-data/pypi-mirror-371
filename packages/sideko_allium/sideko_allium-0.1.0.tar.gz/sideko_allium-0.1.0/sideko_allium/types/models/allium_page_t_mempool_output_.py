import pydantic
import typing

from .t_mempool_output import TMempoolOutput


class AlliumPageTMempoolOutput_(pydantic.BaseModel):
    """
    AlliumPageTMempoolOutput_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[TMempoolOutput] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
