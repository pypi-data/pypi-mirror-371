import typing
import typing_extensions

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
)
from sideko_allium.types import models, params


class HistoryClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get(
        self,
        *,
        addresses: typing.List[params.PayloadAddressHoldingsByToken],
        end_timestamp: str,
        granularity: typing_extensions.Literal["1d", "1h"],
        start_timestamp: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeUnionHistoricalPnlByTokenNoneType_:
        """
        Get Pnl By Token With Historical Breakdown

        POST /api/v1/developer/wallet/pnl-by-token/history

        Args:
            addresses: typing.List[PayloadAddressHoldingsByToken]
            end_timestamp: str
            granularity: typing_extensions.Literal["1d", "1h"]
            start_timestamp: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.wallet.pnl_by_token.history.get(
            addresses=[
                {
                    "address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp",
                    "chain": "solana",
                    "token_address": "So11111111111111111111111111111111111111112",
                }
            ],
            end_timestamp="2025-04-10T00:00:00Z",
            granularity="1h",
            start_timestamp="2025-04-01T00:00:00Z",
        )
        ```
        """
        _json = to_encodable(
            item={
                "addresses": addresses,
                "end_timestamp": end_timestamp,
                "granularity": granularity,
                "start_timestamp": start_timestamp,
            },
            dump_with=params._SerializerPayloadHistoricalPnlByToken,
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/pnl-by-token/history",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.ResponseEnvelopeUnionHistoricalPnlByTokenNoneType_,
            request_options=request_options or default_request_options(),
        )


class AsyncHistoryClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get(
        self,
        *,
        addresses: typing.List[params.PayloadAddressHoldingsByToken],
        end_timestamp: str,
        granularity: typing_extensions.Literal["1d", "1h"],
        start_timestamp: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeUnionHistoricalPnlByTokenNoneType_:
        """
        Get Pnl By Token With Historical Breakdown

        POST /api/v1/developer/wallet/pnl-by-token/history

        Args:
            addresses: typing.List[PayloadAddressHoldingsByToken]
            end_timestamp: str
            granularity: typing_extensions.Literal["1d", "1h"]
            start_timestamp: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.wallet.pnl_by_token.history.get(
            addresses=[
                {
                    "address": "125Z6k4ZAxsgdG7JxrKZpwbcS1rxqpAeqM9GSCKd66Wp",
                    "chain": "solana",
                    "token_address": "So11111111111111111111111111111111111111112",
                }
            ],
            end_timestamp="2025-04-10T00:00:00Z",
            granularity="1h",
            start_timestamp="2025-04-01T00:00:00Z",
        )
        ```
        """
        _json = to_encodable(
            item={
                "addresses": addresses,
                "end_timestamp": end_timestamp,
                "granularity": granularity,
                "start_timestamp": start_timestamp,
            },
            dump_with=params._SerializerPayloadHistoricalPnlByToken,
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/pnl-by-token/history",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.ResponseEnvelopeUnionHistoricalPnlByTokenNoneType_,
            request_options=request_options or default_request_options(),
        )
