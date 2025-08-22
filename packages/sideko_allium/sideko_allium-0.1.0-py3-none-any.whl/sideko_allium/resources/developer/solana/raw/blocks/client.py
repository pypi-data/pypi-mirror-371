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


class BlocksClient:
    def __init__(self, *, base_client: SyncBaseClient):
        self._base_client = base_client

    def list(
        self,
        *,
        page: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        size: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsSolanaBlockTBlock_:
        """
        Get Blocks

        GET /api/v1/developer/solana/raw/blocks

        Args:
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
        client.developer.solana.raw.blocks.list()
        ```
        """
        _query: QueryParams = {}
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
            path="/api/v1/developer/solana/raw/blocks",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsSolanaBlockTBlock_,
            request_options=request_options or default_request_options(),
        )

    def get(
        self,
        *,
        block_slot: int,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsSolanaBlockTBlock:
        """
        Get Block

        GET /api/v1/developer/solana/raw/blocks/{block_slot}

        Args:
            block_slot: int
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        client.developer.solana.raw.blocks.get(block_slot=123)
        ```
        """
        return self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/solana/raw/blocks/{block_slot}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsSolanaBlockTBlock,
            request_options=request_options or default_request_options(),
        )


class AsyncBlocksClient:
    def __init__(self, *, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def list(
        self,
        *,
        page: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        size: typing.Union[
            typing.Optional[int], type_utils.NotGiven
        ] = type_utils.NOT_GIVEN,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsSolanaBlockTBlock_:
        """
        Get Blocks

        GET /api/v1/developer/solana/raw/blocks

        Args:
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
        await client.developer.solana.raw.blocks.list()
        ```
        """
        _query: QueryParams = {}
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
            path="/api/v1/developer/solana/raw/blocks",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            query_params=_query,
            cast_to=models.ApiServerAppCorePaginationAlliumPageSharedLibTortoiseModelsSolanaBlockTBlock_,
            request_options=request_options or default_request_options(),
        )

    async def get(
        self,
        *,
        block_slot: int,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsSolanaBlockTBlock:
        """
        Get Block

        GET /api/v1/developer/solana/raw/blocks/{block_slot}

        Args:
            block_slot: int
            request_options: Additional options to customize the HTTP request

        Returns:
            Successful Response

        Raises:
            ApiError: A custom exception class that provides additional context
                for API errors, including the HTTP status code and response body.

        Examples:
        ```py
        await client.developer.solana.raw.blocks.get(block_slot=123)
        ```
        """
        return await self._base_client.request(
            method="GET",
            path=f"/api/v1/developer/solana/raw/blocks/{block_slot}",
            auth_names=["APIKeyBearer", "APIKeyBearer", "FirebaseAuthBearer"],
            cast_to=models.TortoiseContribPydanticCreatorSharedLibTortoiseModelsSolanaBlockTBlock,
            request_options=request_options or default_request_options(),
        )
