import pydantic
import typing


class NftTokenAttribute(pydantic.BaseModel):
    """
    NftTokenAttribute
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    key: typing.Optional[str] = pydantic.Field(alias="key", default=None)
    value: typing.Optional[typing.Union[str, int, float]] = pydantic.Field(
        alias="value", default=None
    )
