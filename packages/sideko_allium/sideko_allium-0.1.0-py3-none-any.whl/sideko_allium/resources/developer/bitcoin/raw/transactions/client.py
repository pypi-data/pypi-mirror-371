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
from sideko_allium.types import models


class TransactionsClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list(
        self,
        *,
        block_hash: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        page: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        size: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.AlliumPageTTransaction_:
        """
        Get Transactions

        GET /api/v1/developer/bitcoin/raw/transactions

        Args:
            block_hash: typing.Optional[str]
            page: Page number
            size: Page size
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.bitcoin.raw.transactions.list()
        ```
        """
        _query: QueryParams = {}
        if not isinstance(block_hash, type_utils.NotGiven):
            encode_query_param(
                _query,
                "block_hash",
                to_encodable(item=block_hash, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        if not isinstance(page, type_utils.NotGiven):
            encode_query_param(
                _query,
                "page",
                to_encodable(item=page, dump_with=int),
                style="form",
                explode=True,
            )
        if not isinstance(size, type_utils.NotGiven):
            encode_query_param(
                _query,
                "size",
                to_encodable(item=size, dump_with=int),
                style="form",
                explode=True,
            )
        return self._base_client.request(
            method="GET",
            path="/api/v1/developer/bitcoin/raw/transactions",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.AlliumPageTTransaction_,
            request_options=request_options or default_request_options(),
        )

    def get(
        self,
        *,
        transaction_hash: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.TTransaction:
        """
        Get Transaction

        GET /api/v1/developer/bitcoin/raw/transactions/{transaction_hash}

        Args:
            transaction_hash: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.bitcoin.raw.transactions.get(transaction_hash="string")
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/bitcoin/raw/transactions/{transaction_hash}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.TTransaction,
            request_options=request_options or default_request_options(),
        )


class AsyncTransactionsClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
        self,
        *,
        block_hash: typing.Union[
            typing.Optional[str], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        page: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        size: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.AlliumPageTTransaction_:
        """
        Get Transactions

        GET /api/v1/developer/bitcoin/raw/transactions

        Args:
            block_hash: typing.Optional[str]
            page: Page number
            size: Page size
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.bitcoin.raw.transactions.list()
        ```
        """
        _query: QueryParams = {}
        if not isinstance(block_hash, type_utils.NotGiven):
            encode_query_param(
                _query,
                "block_hash",
                to_encodable(item=block_hash, dump_with=typing.Optional[str]),
                style="form",
                explode=True,
            )
        if not isinstance(page, type_utils.NotGiven):
            encode_query_param(
                _query,
                "page",
                to_encodable(item=page, dump_with=int),
                style="form",
                explode=True,
            )
        if not isinstance(size, type_utils.NotGiven):
            encode_query_param(
                _query,
                "size",
                to_encodable(item=size, dump_with=int),
                style="form",
                explode=True,
            )
        return await self._base_client.request(
            method="GET",
            path="/api/v1/developer/bitcoin/raw/transactions",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.AlliumPageTTransaction_,
            request_options=request_options or default_request_options(),
        )

    async def get(
        self,
        *,
        transaction_hash: str,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.TTransaction:
        """
        Get Transaction

        GET /api/v1/developer/bitcoin/raw/transactions/{transaction_hash}

        Args:
            transaction_hash: str
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.bitcoin.raw.transactions.get(transaction_hash="string")
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/bitcoin/raw/transactions/{transaction_hash}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.TTransaction,
            request_options=request_options or default_request_options(),
        )
