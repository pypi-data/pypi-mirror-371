import pydantic
import typing


class ResponseWithId(pydantic.BaseModel):
    """
    ResponseWithId
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    message: str = pydantic.Field(
        alias="message",
    )
    result_id: typing.Optional[str] = pydantic.Field(alias="result_id", default=None)
