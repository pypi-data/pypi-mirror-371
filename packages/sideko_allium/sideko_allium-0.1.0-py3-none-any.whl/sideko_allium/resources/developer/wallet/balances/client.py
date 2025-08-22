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
from sideko_allium.resources.developer.wallet.balances.history import (
    AsyncHistoryClient,
    HistoryClient,
)
from sideko_allium.types import models, params


class BalancesClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client
        self.history = HistoryClient(base_client=self._base_client)

    def get(
        self,
        *,
        data: typing.List[params.PayloadAddress],
        with_liquidity_info: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.WalletLatestBalancesNewEnvelope:
        """
        Latest Fungible Token Balances

        Get the latest balances for a list of wallets.

        POST /api/v1/developer/wallet/balances

        Args:
            with_liquidity_info: If true, returns total_liquidity_usd as well. See https://docs.allium.so/developer/data-tips#token-liquidity for more details.
            data: List of wallet chain+address pairs to get balances for.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.wallet.balances.get(
            data=[{"address": "string", "chain": "string"}]
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(with_liquidity_info, type_utils.NotGiven):
            encode_query_param(
                _query,
                "with_liquidity_info",
                to_encodable(item=with_liquidity_info, dump_with=bool),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerPayloadAddress]
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/balances",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.WalletLatestBalancesNewEnvelope,
            request_options=request_options or default_request_options(),
        )


class AsyncBalancesClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client
        self.history = AsyncHistoryClient(base_client=self._base_client)

    async def get(
        self,
        *,
        data: typing.List[params.PayloadAddress],
        with_liquidity_info: typing.Union[
            typing.Optional[bool], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.WalletLatestBalancesNewEnvelope:
        """
        Latest Fungible Token Balances

        Get the latest balances for a list of wallets.

        POST /api/v1/developer/wallet/balances

        Args:
            with_liquidity_info: If true, returns total_liquidity_usd as well. See https://docs.allium.so/developer/data-tips#token-liquidity for more details.
            data: List of wallet chain+address pairs to get balances for.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.wallet.balances.get(
            data=[{"address": "string", "chain": "string"}]
        )
        ```
        """
        _query: QueryParams = {}
        if not isinstance(with_liquidity_info, type_utils.NotGiven):
            encode_query_param(
                _query,
                "with_liquidity_info",
                to_encodable(item=with_liquidity_info, dump_with=bool),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerPayloadAddress]
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/balances",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.WalletLatestBalancesNewEnvelope,
            request_options=request_options or default_request_options(),
        )
