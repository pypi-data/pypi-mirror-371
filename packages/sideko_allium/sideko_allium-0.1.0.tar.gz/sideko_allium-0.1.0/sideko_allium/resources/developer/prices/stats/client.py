import typing

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
)
from sideko_allium.types import models, params


class StatsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get(
        self,
        *,
        data: typing.List[params.PayloadTokenAddress],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.EnvelopeTokenStats_:
        """
        Token Stats

        Get the stats for the given token addresseses.

        POST /api/v1/developer/prices/stats

        Args:
            data: List of token addresses to get stats for.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.prices.stats.get(
            data=[{"chain": "string", "token_address": "string"}]
        )
        ```
        """
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerPayloadTokenAddress]
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/prices/stats",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            json=_json,
            cast_to=models.EnvelopeTokenStats_,
            request_options=request_options or default_request_options(),
        )


class AsyncStatsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get(
        self,
        *,
        data: typing.List[params.PayloadTokenAddress],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.EnvelopeTokenStats_:
        """
        Token Stats

        Get the stats for the given token addresseses.

        POST /api/v1/developer/prices/stats

        Args:
            data: List of token addresses to get stats for.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.prices.stats.get(
            data=[{"chain": "string", "token_address": "string"}]
        )
        ```
        """
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerPayloadTokenAddress]
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/prices/stats",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            json=_json,
            cast_to=models.EnvelopeTokenStats_,
            request_options=request_options or default_request_options(),
        )
