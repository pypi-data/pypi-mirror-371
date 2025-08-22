import pydantic
import typing


class FilterResponse(pydantic.BaseModel):
    """
    FilterResponse
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    filter: typing.Dict[str, typing.Any] = pydantic.Field(
        alias="filter",
    )
    id: str = pydantic.Field(
        alias="id",
    )
