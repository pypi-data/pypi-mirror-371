import pydantic
import typing


class PnlByWalletUnrealizedPnlRatioChange(pydantic.BaseModel):
    """
    PnlByWalletUnrealizedPnlRatioChange
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        extra="allow",
    )

    __pydantic_extra__: typing.Dict[str, typing.Optional[float]]
