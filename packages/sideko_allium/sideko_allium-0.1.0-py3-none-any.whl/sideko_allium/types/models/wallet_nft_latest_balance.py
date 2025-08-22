import pydantic
import typing

from .nft_token import NftToken


class WalletNftLatestBalance(pydantic.BaseModel):
    """
    WalletNftLatestBalance
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    acquired_at: typing.Optional[str] = pydantic.Field(
        alias="acquired_at", default=None
    )
    address: str = pydantic.Field(
        alias="address",
    )
    balance: int = pydantic.Field(
        alias="balance",
    )
    chain: str = pydantic.Field(
        alias="chain",
    )
    nft_token: typing.Optional[NftToken] = pydantic.Field(
        alias="nft_token", default=None
    )
    token_address: str = pydantic.Field(
        alias="token_address",
    )
    token_id: typing.Optional[str] = pydantic.Field(
        alias="token_id",
    )
