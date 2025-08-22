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


class TransactionsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def get(
        self,
        *,
        data: typing.List[params.PayloadAddress],
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        lookback_days: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        transaction_hash: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.WalletTransactionsEnvelope:
        """
        Transactions

        Provides enriched transaction history data for wallet(s).

        POST /api/v1/developer/wallet/transactions

        Args:
            cursor: typing.Optional[str]
            limit: Limit the number of transactions returned. Default is 25.
            lookback_days: typing.Optional[int]
            transaction_hash: typing.Optional[str]
            data: List of chain+addresses to get transactions for.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.wallet.transactions.get(
            data=[
                {
                    "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
                    "chain": "ethereum",
                }
            ]
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
        if not isinstance(limit, type_utils.NotGiven):
            encode_query_param(
                _query,
                "limit",
                to_encodable(item=limit, dump_with=int),
                style="form",
                explode=True,
            )
        if not isinstance(lookback_days, type_utils.NotGiven):
            encode_query_param(
                _query,
                "lookback_days",
                to_encodable(item=lookback_days, dump_with=typing.Optional[int]),
                style="form",
                explode=True,
            )
        if not isinstance(transaction_hash, type_utils.NotGiven):
            encode_query_param(
                _query,
                "transaction_hash",
                to_encodable(item=transaction_hash, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerPayloadAddress]
        )
        return self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/transactions",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.WalletTransactionsEnvelope,
            request_options=request_options or default_request_options(),
        )


class AsyncTransactionsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def get(
        self,
        *,
        data: typing.List[params.PayloadAddress],
        cursor: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        limit: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        lookback_days: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        transaction_hash: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.WalletTransactionsEnvelope:
        """
        Transactions

        Provides enriched transaction history data for wallet(s).

        POST /api/v1/developer/wallet/transactions

        Args:
            cursor: typing.Optional[str]
            limit: Limit the number of transactions returned. Default is 25.
            lookback_days: typing.Optional[int]
            transaction_hash: typing.Optional[str]
            data: List of chain+addresses to get transactions for.
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.wallet.transactions.get(
            data=[
                {
                    "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
                    "chain": "ethereum",
                }
            ]
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
        if not isinstance(limit, type_utils.NotGiven):
            encode_query_param(
                _query,
                "limit",
                to_encodable(item=limit, dump_with=int),
                style="form",
                explode=True,
            )
        if not isinstance(lookback_days, type_utils.NotGiven):
            encode_query_param(
                _query,
                "lookback_days",
                to_encodable(item=lookback_days, dump_with=typing.Optional[int]),
                style="form",
                explode=True,
            )
        if not isinstance(transaction_hash, type_utils.NotGiven):
            encode_query_param(
                _query,
                "transaction_hash",
                to_encodable(item=transaction_hash, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        _json = to_encodable(
            item=data, dump_with=typing.List[params._SerializerPayloadAddress]
        )
        return await self._base_client.request(
            method="POST",
            path="/api/v1/developer/wallet/transactions",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            json=_json,
            cast_to=models.WalletTransactionsEnvelope,
            request_options=request_options or default_request_options(),
        )
