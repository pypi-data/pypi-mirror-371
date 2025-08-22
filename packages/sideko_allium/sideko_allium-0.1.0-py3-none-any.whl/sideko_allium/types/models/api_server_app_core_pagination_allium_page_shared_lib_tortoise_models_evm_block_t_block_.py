import pydantic
import typing

from .tortoise_contrib_pydantic_creator_shared_lib_tortoise_models_evm_block_t_block import (
    TortoiseContribPydanticCreatorSharedLibTortoiseModelsEvmBlockTBlock,
)


class ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsEvmBlockTBlock_(
    pydantic.BaseModel
):
    """
    ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsEvmBlockTBlock_
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    items: typing.List[
        TortoiseContribPydanticCreatorSharedLibTortoiseModelsEvmBlockTBlock
    ] = pydantic.Field(
        alias="items",
    )
    page: typing.Optional[int] = pydantic.Field(alias="page", default=None)
    size: int = pydantic.Field(
        alias="size",
    )
