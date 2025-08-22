import pydantic
import typing
import typing_extensions

from .kafka_data_destination_metadata import (
    KafkaDataDestinationMetadata,
    _SerializerKafkaDataDestinationMetadata,
)
from .pub_sub_data_destination_metadata import (
    PubSubDataDestinationMetadata,
    _SerializerPubSubDataDestinationMetadata,
)
from .pub_sub_data_source_metadata import (
    PubSubDataSourceMetadata,
    _SerializerPubSubDataSourceMetadata,
)
from .std_out_data_destination_metadata import (
    StdOutDataDestinationMetadata,
    _SerializerStdOutDataDestinationMetadata,
)


class DataTransformationWorkflowRequest(typing_extensions.TypedDict):
    """
    DataTransformationWorkflowRequest
    """

    data_destination_config: typing_extensions.Required[
        typing.Union[
            KafkaDataDestinationMetadata,
            PubSubDataDestinationMetadata,
            StdOutDataDestinationMetadata,
        ]
    ]

    data_source_config: typing_extensions.Required[PubSubDataSourceMetadata]

    description: typing_extensions.NotRequired[typing.Optional[str]]

    filter_id: typing_extensions.Required[str]


class _SerializerDataTransformationWorkflowRequest(pydantic.BaseModel):
    """
    Serializer for DataTransformationWorkflowRequest handling case conversions
    and file omissions as dictated by the API
    """

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
    )

    data_destination_config: typing.Union[
        _SerializerKafkaDataDestinationMetadata,
        _SerializerPubSubDataDestinationMetadata,
        _SerializerStdOutDataDestinationMetadata,
    ] = pydantic.Field(
        alias="data_destination_config",
    )
    data_source_config: _SerializerPubSubDataSourceMetadata = pydantic.Field(
        alias="data_source_config",
    )
    description: typing.Optional[str] = pydantic.Field(
        alias="description", default=None
    )
    filter_id: str = pydantic.Field(
        alias="filter_id",
    )
