import pydantic
import typing


class AssetAmount(pydantic.BaseModel):
    """
    AssetAmount
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    amount: typing.Optional[float] = pydantic.Field(alias="amount", default=None)
    amount_str: typing.Optional[str] = pydantic.Field(alias="amount_str", default=None)
    raw_amount: typing.Optional[str] = pydantic.Field(
        alias="raw_amount",
    )
