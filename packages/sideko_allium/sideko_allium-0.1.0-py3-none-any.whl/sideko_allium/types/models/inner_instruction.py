import pydantic
import typing


class InnerInstruction(pydantic.BaseModel):
    """
    InnerInstruction
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    accounts: typing.Optional[typing.List[str]] = pydantic.Field(
        alias="accounts",
    )
    data: typing.Optional[str] = pydantic.Field(
        alias="data",
    )
    data_hex: typing.Optional[str] = pydantic.Field(
        alias="data_hex",
    )
    inner_instruction_index: int = pydantic.Field(
        alias="inner_instruction_index",
    )
    instruction_index: int = pydantic.Field(
        alias="instruction_index",
    )
    is_voting: bool = pydantic.Field(
        alias="is_voting",
    )
    parent_instruction_program_id: str = pydantic.Field(
        alias="parent_instruction_program_id",
    )
    parent_tx_signer: str = pydantic.Field(
        alias="parent_tx_signer",
    )
    parent_tx_success: bool = pydantic.Field(
        alias="parent_tx_success",
    )
    parsed: typing.Optional[str] = pydantic.Field(
        alias="parsed",
    )
    parsed_type: typing.Optional[str] = pydantic.Field(
        alias="parsed_type",
    )
    program_id: str = pydantic.Field(
        alias="program_id",
    )
    program_name: typing.Optional[str] = pydantic.Field(
        alias="program_name",
    )
    txn_id: str = pydantic.Field(
        alias="txn_id",
    )
    txn_index: int = pydantic.Field(
        alias="txn_index",
    )
