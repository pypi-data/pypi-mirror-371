import pydantic
import typing
import typing_extensions

from .nft_price import NftPrice


class NftActivity(pydantic.BaseModel):
    """
    NftActivity
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    amount: int = pydantic.Field(
        alias="amount",
    )
    batch_index: int = pydantic.Field(
        alias="batch_index",
    )
    block_timestamp: str = pydantic.Field(
        alias="block_timestamp",
    )
    collection_name: str = pydantic.Field(
        alias="collection_name",
    )
    from_address: str = pydantic.Field(
        alias="from_address",
    )
    log_index: int = pydantic.Field(
        alias="log_index",
    )
    price: typing.Optional[NftPrice] = pydantic.Field(alias="price", default=None)
    to_address: str = pydantic.Field(
        alias="to_address",
    )
    token_address: str = pydantic.Field(
        alias="token_address",
    )
    token_id: typing.Optional[str] = pydantic.Field(alias="token_id", default=None)
    token_name: str = pydantic.Field(
        alias="token_name",
    )
    transaction_hash: str = pydantic.Field(
        alias="transaction_hash",
    )
    type_: typing_extensions.Literal["mint", "sale", "transfer"] = pydantic.Field(
        alias="type",
    )
