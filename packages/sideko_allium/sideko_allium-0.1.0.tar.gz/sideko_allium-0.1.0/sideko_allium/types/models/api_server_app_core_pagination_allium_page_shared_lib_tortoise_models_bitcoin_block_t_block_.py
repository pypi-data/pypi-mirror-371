import pydantic
import typing

from .tortoise_contrib_pydantic_creator_shared_lib_tortoise_models_bitcoin_block_t_block import (
    TortoiseContribPydanticCreatorSharedLibTortoiseModelsBitcoinBlockTBlock,
)


class ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsBitcoinBlockTBlock_(
    pydantic.BaseModel
):
    """
    ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsBitcoinBlockTBlock_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[
        TortoiseContribPydanticCreatorSharedLibTortoiseModelsBitcoinBlockTBlock
    ] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
