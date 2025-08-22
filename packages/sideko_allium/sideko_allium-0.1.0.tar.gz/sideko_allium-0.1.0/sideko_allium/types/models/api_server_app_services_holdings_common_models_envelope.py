import pydantic
import typing

from .aggregated_holdings import AggregatedHoldings


class ApiServerAppServicesHoldingsCommonModelsEnvelope(pydantic.BaseModel):
    """
    ApiServerAppServicesHoldingsCommonModelsEnvelope
    """

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    cursor: typing.Optional[str] = pydantic.Field(alias="cursor", default=None)
    items: typing.List[AggregatedHoldings] = pydantic.Field(
        alias="items",
    )
