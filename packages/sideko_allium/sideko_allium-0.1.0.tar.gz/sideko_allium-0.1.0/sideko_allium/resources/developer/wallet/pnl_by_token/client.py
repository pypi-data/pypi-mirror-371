import typing

from sideko_allium.core import (
    AsyncBaseClient,
    RequestOptions,
    SyncBaseClient,
    default_request_options,
    to_encodable,
)
from sideko_allium.resources.developer.wallet.pnl_by_token.history import (
    AsyncHistoryClient,
    HistoryClient,
)
from sideko_allium.types import models, params


class PnlByTokenClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.history = HistoryClient(base_client=self._base_client)

    def get(
        self,
        *,
        data: typing.List[params.PayloadAddressHoldingsByToken],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeUnionPnlByTokenNoneType_:
        """
        Get Pnl By Token

        POST /api/v1/developer/wallet/pnl-by-token

        Args:
            data: typing.List[PayloadAddressHoldingsByToken]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.wallet.pnl_by_token.get(
            data=[{"address": "string", "chain": "string", "token_address": "string"}]
        )
        ```
        """
        _json = to_encodable(
            item=data,
            dump_with=typing.List[params._SerializerPayloadAddressHoldingsByToken],
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/pnl-by-token",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.ResponseEnvelopeUnionPnlByTokenNoneType_,
            request_options=request_options or default_request_options(),
        )


class AsyncPnlByTokenClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.history = AsyncHistoryClient(base_client=self._base_client)

    async def get(
        self,
        *,
        data: typing.List[params.PayloadAddressHoldingsByToken],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ResponseEnvelopeUnionPnlByTokenNoneType_:
        """
        Get Pnl By Token

        POST /api/v1/developer/wallet/pnl-by-token

        Args:
            data: typing.List[PayloadAddressHoldingsByToken]
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.wallet.pnl_by_token.get(
            data=[{"address": "string", "chain": "string", "token_address": "string"}]
        )
        ```
        """
        _json = to_encodable(
            item=data,
            dump_with=typing.List[params._SerializerPayloadAddressHoldingsByToken],
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/pnl-by-token",
            auth_names=["APIKeyBearer"],
            json=_json,
            cast_to=models.ResponseEnvelopeUnionPnlByTokenNoneType_,
            request_options=request_options or default_request_options(),
        )
