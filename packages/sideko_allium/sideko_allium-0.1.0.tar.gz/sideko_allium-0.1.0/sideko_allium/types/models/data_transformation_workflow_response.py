import pydantic
import typing

from .kafka_data_destination_metadata import KafkaDataDestinationMetadata
from .pub_sub_data_destination_metadata import PubSubDataDestinationMetadata
from .pub_sub_data_source_metadata import PubSubDataSourceMetadata
from .std_out_data_destination_metadata import StdOutDataDestinationMetadata


class DataTransformationWorkflowResponse(pydantic.BaseModel):
    """
    DataTransformationWorkflowResponse
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    data_destination_config: typing.Union[
        KafkaDataDestinationMetadata,
        PubSubDataDestinationMetadata,
        StdOutDataDestinationMetadata,
    ] = pydantic.Field(
        alias="data_destination_config",
    )
    data_source_config: PubSubDataSourceMetadata = pydantic.Field(
        alias="data_source_config",
    )
    description: typing.Optional[str] = pydantic.Field(
        alias="description", default=None
    )
    external_workflow_id: typing.Optional[str] = pydantic.Field(
        alias="external_workflow_id", default=None
    )
    filter_id: str = pydantic.Field(
        alias="filter_id",
    )
    id: typing.Optional[str] = pydantic.Field(alias="id", default=None)
    status: typing.Optional[str] = pydantic.Field(alias="status", default=None)
