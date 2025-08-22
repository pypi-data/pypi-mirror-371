import typing

from sideko_allium.core import (
    AsyncBaseClient,
    QueryParams,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    encode_query_param,
    to_encodable,
    type_utils,
)
from sideko_allium.types import models, params


class HistoryClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list(
        self,
        *,
        data: typing.Union[
            params.PayloadPriceHistorical, params.PayloadPriceHistoricalLegacy
        ],
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.EnvelopeUnionTokenPriceHistoricalTokenPrice_:
        """
        Token Prices History

        Get a list of historical token prices by chain and token address for a given time range and granularity.

        POST /api/v1/developer/prices/history

        Args:
            cursor: typing.Optional[str]
            data: typing.Union[PayloadPriceHistorical, PayloadPriceHistoricalLegacy]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.prices.history.list(
            data={
                "addresses": [
                    {"chain": "string", "token_address": "string"},
                    {"chain": "string", "token_address": "string"},
                ],
                "end_timestamp": "2025-03-07T01:00:00Z",
                "start_timestamp": "2025-03-07T00:00:00Z",
                "time_granularity": "5m",
            }
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(cursor, type_utils.NotGiven):
            encode_query_param(
                _query,
                "cursor",
                to_encodable(item=cursor, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item=data,
            dump_with=typing.Union[
                params._SerializerPayloadPriceHistorical,
                params._SerializerPayloadPriceHistoricalLegacy,
            ],
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/prices/history",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.EnvelopeUnionTokenPriceHistoricalTokenPrice_,
            request_options=request_options or default_request_options(),
        )


class AsyncHistoryClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
        self,
        *,
        data: typing.Union[
            params.PayloadPriceHistorical, params.PayloadPriceHistoricalLegacy
        ],
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.EnvelopeUnionTokenPriceHistoricalTokenPrice_:
        """
        Token Prices History

        Get a list of historical token prices by chain and token address for a given time range and granularity.

        POST /api/v1/developer/prices/history

        Args:
            cursor: typing.Optional[str]
            data: typing.Union[PayloadPriceHistorical, PayloadPriceHistoricalLegacy]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.prices.history.list(
            data={
                "addresses": [
                    {"chain": "string", "token_address": "string"},
                    {"chain": "string", "token_address": "string"},
                ],
                "end_timestamp": "2025-03-07T01:00:00Z",
                "start_timestamp": "2025-03-07T00:00:00Z",
                "time_granularity": "5m",
            }
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(cursor, type_utils.NotGiven):
            encode_query_param(
                _query,
                "cursor",
                to_encodable(item=cursor, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item=data,
            dump_with=typing.Union[
                params._SerializerPayloadPriceHistorical,
                params._SerializerPayloadPriceHistoricalLegacy,
            ],
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/prices/history",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.EnvelopeUnionTokenPriceHistoricalTokenPrice_,
            request_options=request_options or default_request_options(),
        )
