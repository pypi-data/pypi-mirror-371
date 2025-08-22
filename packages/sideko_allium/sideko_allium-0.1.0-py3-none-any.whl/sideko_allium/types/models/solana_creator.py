import pydantic
import typing


class SolanaCreator(pydantic.BaseModel):
    """
    SolanaCreator
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    address: typing.Optional[str] = pydantic.Field(alias="address", default=None)
    share: typing.Optional[int] = pydantic.Field(alias="share", default=None)
    verified: typing.Optional[int] = pydantic.Field(alias="verified", default=None)
