import pydantic
import typing_extensions


class NotionalAmount(pydantic.BaseModel):
    """
    NotionalAmount
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    amount: float = pydantic.Field(
        alias="amount",
    )
    currency: typing_extensions.Literal["USD"] = pydantic.Field(
        alias="currency",
    )
