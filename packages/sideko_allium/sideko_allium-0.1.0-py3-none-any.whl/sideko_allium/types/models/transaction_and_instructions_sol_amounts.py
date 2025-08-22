import pydantic
import typing

from .transaction_and_instructions_sol_amounts_additional_props import (
    TransactionAndInstructionsSolAmountsAdditionalProps,
)


class TransactionAndInstructionsSolAmounts(pydantic.BaseModel):
    """
    TransactionAndInstructionsSolAmounts
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[
        str, TransactionAndInstructionsSolAmountsAdditionalProps
    ]
