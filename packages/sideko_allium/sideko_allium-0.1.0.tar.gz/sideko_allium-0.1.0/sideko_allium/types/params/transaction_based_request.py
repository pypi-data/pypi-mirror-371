import pydantic
import typing_extensions


class TransactionBasedRequest(typing_extensions.TypedDict):
    """
    TransactionBasedRequest
    """

    block_timestamp: typing_extensions.Required[str]

    txn_id: typing_extensions.Required[str]


class _SerializerTransactionBasedRequest(pydantic.BaseModel):
    """
    Serializer for TransactionBasedRequest handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    block_timestamp: str = pydantic.Field(
        alias="block_timestamp",
    )
    txn_id: str = pydantic.Field(
        alias="txn_id",
    )
