import pydantic
import typing

from .account_key import AccountKey
from .token_balance import TokenBalance
from .transaction_mint_to_decimals import TransactionMintToDecimals
from .transaction_sol_amounts import TransactionSolAmounts
from .transaction_token_accounts import TransactionTokenAccounts


class Transaction(pydantic.BaseModel):
    """
    Transaction
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    account_keys: typing.List[AccountKey] = pydantic.Field(
        alias="account_keys",
    )
    block_hash: str = pydantic.Field(
        alias="block_hash",
    )
    block_height: int = pydantic.Field(
        alias="block_height",
    )
    block_slot: int = pydantic.Field(
        alias="block_slot",
    )
    block_timestamp: str = pydantic.Field(
        alias="block_timestamp",
    )
    fee: int = pydantic.Field(
        alias="fee",
    )
    instruction_count: int = pydantic.Field(
        alias="instruction_count",
    )
    is_voting: bool = pydantic.Field(
        alias="is_voting",
    )
    log_messages: typing.List[str] = pydantic.Field(
        alias="log_messages",
    )
    mint_to_decimals: TransactionMintToDecimals = pydantic.Field(
        alias="mint_to_decimals",
    )
    post_balances: typing.List[int] = pydantic.Field(
        alias="post_balances",
    )
    post_token_balances: typing.List[TokenBalance] = pydantic.Field(
        alias="post_token_balances",
    )
    pre_balances: typing.List[int] = pydantic.Field(
        alias="pre_balances",
    )
    pre_token_balances: typing.List[TokenBalance] = pydantic.Field(
        alias="pre_token_balances",
    )
    pubkeys: typing.List[str] = pydantic.Field(
        alias="pubkeys",
    )
    recent_block_hash: str = pydantic.Field(
        alias="recent_block_hash",
    )
    signatures: typing.List[str] = pydantic.Field(
        alias="signatures",
    )
    signer: str = pydantic.Field(
        alias="signer",
    )
    sol_amounts: TransactionSolAmounts = pydantic.Field(
        alias="sol_amounts",
    )
    success: bool = pydantic.Field(
        alias="success",
    )
    token_accounts: TransactionTokenAccounts = pydantic.Field(
        alias="token_accounts",
    )
    txn_id: str = pydantic.Field(
        alias="txn_id",
    )
    txn_index: int = pydantic.Field(
        alias="txn_index",
    )
