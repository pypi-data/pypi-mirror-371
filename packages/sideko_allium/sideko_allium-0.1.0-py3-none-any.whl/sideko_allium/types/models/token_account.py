import pydantic
import typing


class TokenAccount(pydantic.BaseModel):
    """
    TokenAccount
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    account: typing.Optional[str] = pydantic.Field(alias="account", default=None)
    account_index: typing.Optional[int] = pydantic.Field(
        alias="account_index", default=None
    )
    mint: typing.Optional[str] = pydantic.Field(alias="mint", default=None)
    owner: typing.Optional[str] = pydantic.Field(alias="owner", default=None)
    program_id: typing.Optional[str] = pydantic.Field(alias="program_id", default=None)
