import pydantic
import typing


class StdOutDataDestinationMetadata(pydantic.BaseModel):
    """
    StdOutDataDestinationMetadata
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
