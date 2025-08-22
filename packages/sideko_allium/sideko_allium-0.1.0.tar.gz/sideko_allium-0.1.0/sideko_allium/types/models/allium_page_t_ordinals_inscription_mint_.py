import pydantic
import typing

from .t_ordinals_inscription_mint import TOrdinalsInscriptionMint


class AlliumPageTOrdinalsInscriptionMint_(pydantic.BaseModel):
    """
    AlliumPageTOrdinalsInscriptionMint_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[TOrdinalsInscriptionMint] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
