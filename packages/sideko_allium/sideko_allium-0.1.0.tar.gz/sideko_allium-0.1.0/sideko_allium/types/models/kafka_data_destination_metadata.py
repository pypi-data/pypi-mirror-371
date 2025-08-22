import pydantic
import typing


class KafkaDataDestinationMetadata(pydantic.BaseModel):
    """
    KafkaDataDestinationMetadata
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    topic: typing.Optional[str] = pydantic.Field(alias="topic", default=None)
    type_: typing.Optional[str] = pydantic.Field(alias="type", default=None)
