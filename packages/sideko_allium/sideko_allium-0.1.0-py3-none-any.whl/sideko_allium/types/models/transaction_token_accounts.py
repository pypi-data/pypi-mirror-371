import pydantic
import typing

from .token_account import TokenAccount


class TransactionTokenAccounts(pydantic.BaseModel):
    """
    TransactionTokenAccounts
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, TokenAccount]
