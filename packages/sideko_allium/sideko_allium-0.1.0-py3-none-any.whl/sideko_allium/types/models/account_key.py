import pydantic


class AccountKey(pydantic.BaseModel):
    """
    AccountKey
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    pubkey: str = pydantic.Field(
        alias="pubkey",
    )
    signer: bool = pydantic.Field(
        alias="signer",
    )
    source: str = pydantic.Field(
        alias="source",
    )
    writable: bool = pydantic.Field(
        alias="writable",
    )
