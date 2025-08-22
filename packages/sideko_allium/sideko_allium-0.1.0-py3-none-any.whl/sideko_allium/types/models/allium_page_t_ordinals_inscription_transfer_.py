import pydantic
import typing

from .t_ordinals_inscription_transfer import TOrdinalsInscriptionTransfer


class AlliumPageTOrdinalsInscriptionTransfer_(pydantic.BaseModel):
    """
    AlliumPageTOrdinalsInscriptionTransfer_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[TOrdinalsInscriptionTransfer] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
