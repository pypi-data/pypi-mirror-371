import pydantic
import typing

from .transaction_sol_amounts_additional_props import (
    TransactionSolAmountsAdditionalProps,
)


class TransactionSolAmounts(pydantic.BaseModel):
    """
    TransactionSolAmounts
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, TransactionSolAmountsAdditionalProps]
